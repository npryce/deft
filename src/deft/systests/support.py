
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
from deft.storage import FileStorage
from deft.memstorage import MemStorage
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
        return Rows([[row[c] for c in col_indices] for row in self.rows])
    
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
        return Rows([line.split(" ") for line in self.lines])
    
    @property
    def value(self):
        return self.stdout.strip()
    
    @property
    def stderr_lines(self):
        return self.stderr.splitlines()


class ProcessError(Exception, ProcessResult):
    def __init__(self, command, status, stdout, stderr):
        Exception.__init__(self, stderr)
        ProcessResult.__init__(self, command, status, stdout, stderr)



class SystestEnvironment(object):
    description = "real environment"
    
    def __init__(self, name):
        self.testdir = os.path.join("output", "testing", "systest", name)
        self.storage = FileStorage(self.testdir)
        ensure_empty_dir_exists(self.testdir)
    
    def abspath(self, subpath):
        return os.path.abspath(os.path.join(self.testdir, subpath))
        
    def deft(self, *args, **kwargs):
        env = {
            'PYTHONPATH': os.path.abspath("src"),
            'DEFT_EDITOR': self.fake_editor_command(kwargs.get('editor_input', 'description-not-important'))
        }
        
        return self.run(command=["deft"]+list(args), env_override=env)
    
    def run(self, command, env_override={}):
        path = os.pathsep.join([os.path.abspath('python-dev/bin'),
                                os.path.abspath(os.getcwd()),
                                os.defpath])
        
        env = {'PATH': path}
        env.update(env_override)
        
        process = Popen(command, 
                        stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                        close_fds=True, 
                        cwd=self.testdir,
                        env=env)
        
        (stdout, stderr) = process.communicate()
        
        if process.returncode == 0:
            return ProcessResult(command, process.returncode, stdout, stderr)
        else:
            raise ProcessError(command, process.returncode, stdout, stderr)
    
    def fake_editor_command(self, input):
        return os.path.abspath("testing-tools/fake-editor") + " " + repr(input)


class InMemoryEnvironment(object):
    description = "in-memory environment"
    
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
            self.storage.save_text(self.storage.relpath(path), editor_content)
        
        cli = CommandLineInterface(self, out=stdout, err=stderr, editor=fake_editor)
        try:
            cli.run(command)
            return ProcessResult(command, 0, stdout.getvalue(), stderr.getvalue())
        except UserError:
            raise ProcessError(command, 1, stdout.getvalue(), 
                               traceback.format_exc() + "\n\nstderr:\n\n" + stderr.getvalue())
    
    def init_tracker(self, **config_overrides):
        return init_with_storage(self.storage, config_overrides)
    
    def load_tracker(self):
        return load_with_storage(self.storage)

    def abspath(self, subpath):
        return self.storage.abspath(subpath)
    
    

def dynamically_selected_environment(test_name):
    env_name = os.getenv("DEFT_SYSTEST_ENV")
    
    if env_name is None or env_name is "" or env_name == "real":
        return SystestEnvironment(test_name)
    if env_name == "mem":
        return InMemoryEnvironment(test_name)
    else:
        raise ValueError("unknown environment %s, must be one of 'mem', 'real'"%env_name)


def systest(test_func, env=dynamically_selected_environment):
    @wraps(test_func)
    def run_with_environment():
        test_func(env(test_func.__module__ + "." + test_func.func_name))
    
    return compose(istest, attr('systest'))(run_with_environment)



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
