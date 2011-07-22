
import sys
from abc import ABCMeta, abstractmethod
import traceback
from StringIO import StringIO
import os
import shutil
from subprocess import Popen, PIPE, CalledProcessError
from functools import wraps
from functional import compose
from nose.tools import istest, nottest
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from deft.fileops import *
from deft.formats import YamlFormat
from deft.storage.filesystem import FileStorage
from deft.storage.memory import MemStorage
from deft.cli import CommandLineInterface
from deft.tracker import FeatureTracker, UserError, init_with_storage, load_with_storage

Deft = os.path.abspath("deft")


class Rows:
    def __init__(self, rows):
        self.rows = rows
    
    def __len__(self):
        return len(self.rows)
    
    def __getitem__(self, i):
        return self.rows[i]
    
    def __iter__(self):
        return iter(self.rows)
    
    def cols(self, *col_indices):
        try: 
            return Rows([[row[c] for c in col_indices] for row in self.rows])
        except IndexError as e:
            raise IndexError("cannot select column indices " + str(col_indices) + " from " + str(self.rows))
    
    def __eq__(self, other):
        return list(self) == list(other)
    
    def __str__(self):
        return str(self.rows)
    


class ProcessResult(object):
    def __init__(self, command, status, stdout, stderr):
        self.command = command
        self.status = status
        self.stdout = stdout
        self.stderr = stderr

    @property
    def lines(self):
        return self.stdout.splitlines()
    
    @property
    def rows(self):
        return Rows([line.split() for line in self.lines])
    
    @property
    def value(self):
        return self.stdout.strip()
    
    @property
    def yaml(self):
        return YamlFormat.load(StringIO(self.stdout))
    
    @property
    def stderr_lines(self):
        return self.stderr.splitlines()


class ProcessError(Exception, ProcessResult):
    def __init__(self, command, status, stdout, stderr):
        Exception.__init__(self, stderr)
        ProcessResult.__init__(self, command, status, stdout, stderr)


class OutOfProcessEnvironment(object):
    __metaclass__ = ABCMeta
    
    @classmethod
    def attribute(selfclass, test_func):
        test_func.fileio = 1
    
    def __init__(self, name):
        self.testdir = os.path.join("output", "testing", "systest", name)
        self.storage = FileStorage(self.testdir)
        ensure_empty_dir_exists(self.testdir)
    
    def abspath(self, subpath):
        return os.path.abspath(os.path.join(self.testdir, subpath))
    
    def makedirs(self, subpath):
        return os.makedirs(self.abspath(subpath))
        
    def deft(self, *args, **kwargs):
        env = {
            'PYTHONPATH': os.path.abspath("src"),
            'DEFT_EDITOR': self.fake_editor_command(kwargs.get('editor_input', 'description-not-important'))
        }
        
        cwd_subdir = kwargs.get("cwd", ".")
        
        return self.run(command=["deft"]+list(args), 
                        env_override=env, 
                        cwd=self.abspath(cwd_subdir))
    
    @abstractmethod
    def binpath(self):
        pass
    
    def run(self, command, env_override={}, cwd=None):
        env = {'PATH': self.binpath()}
        env.update(env_override)
        
        process = Popen(command, 
                        stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                        close_fds=True, 
                        cwd=cwd or self.testdir,
                        env=env)
        
        (stdout, stderr) = process.communicate()
        
        if process.returncode == 0:
            return ProcessResult(command, process.returncode, stdout, stderr)
        else:
            raise ProcessError(command, process.returncode, stdout, stderr)
    
    def fake_editor_command(self, input):
        return os.path.abspath("testing-tools/fake-editor") + " " + repr(input)


class DevEnvironment(OutOfProcessEnvironment):
    def binpath(self):
        return os.pathsep.join([os.path.abspath("bin"),
                                os.defpath])


class InstallTestEnvironment(OutOfProcessEnvironment):
    def binpath(self):
        return os.pathsep.join([os.path.abspath('output/install/bin'),
                                os.defpath])

class InMemoryEnvironment(object):
    @classmethod
    def attribute(selfclass, test_func):
        pass
    
    def __init__(self, name):
        self.name = name
        self.storage = MemStorage("testing")
        self.editor_content = ""
    
    def deft(self, *args, **kwargs):
        command = ["deft"] + list(args)
        
        editor_content = kwargs.get('editor_input', 'description-not-important')
        stdout = StringIO()
        stderr = StringIO()
        
        def fake_editor(path):
            relpath = self.storage.relpath(path)
            with self.storage.open(relpath, "w") as output:
                output.write(editor_content)
        
        cli = CommandLineInterface(self, out=stdout, err=stderr, editor=fake_editor)
        try:
            cli.run(command)
            return ProcessResult(command, 0, stdout.getvalue(), stderr.getvalue())
        except UserError:
            raise ProcessError(command, 1, stdout.getvalue(), 
                               traceback.format_exc() + "\n\nstderr:\n\n" + stderr.getvalue())
    
    def init_tracker(self, warning_listener, **config_overrides):
        return init_with_storage(self.storage, warning_listener, config_overrides)
    
    def load_tracker(self, warning_listener):
        return load_with_storage(self.storage, warning_listener)
    
    def abspath(self, subpath):
        return self.storage.abspath(subpath)
    
    

def select_environment_from_envvar():
    env_name = os.getenv("DEFT_SYSTEST_ENV")
    
    if env_name is None or env_name is "" or env_name == "dev":
        return DevEnvironment
    elif env_name == "mem":
        return InMemoryEnvironment
    elif env_name == "install":
        return InstallTestEnvironment
    else:
        raise ValueError("unknown environment %s, must be one of 'mem', 'dev', 'install' (defaults to 'dev')"%env_name)

_selected_environment = select_environment_from_envvar()

def systest_in(environment):
    def decorator(test_func):
        @wraps(test_func)
        def run_with_environment():
            env = environment(test_func.__module__ + "." + test_func.func_name)
            test_func(env)
            
        environment.attribute(run_with_environment)
        return istest(run_with_environment)
    
    return decorator

systest = systest_in(_selected_environment)



def wip(f):
    @wraps(f)
    def run_test(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            raise SkipTest("WIP test failed: " + str(e))
        fail("test passed but marked as work in progress")
    
    return attr('wip')(run_test)



def fail(message):
    raise AssertionError(message)
