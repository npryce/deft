
import inspect
import os
import shutil
from subprocess import Popen, PIPE, CalledProcessError
from functools import wraps
from functional import compose
from nose.tools import istest, nottest
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from deft.fileops import *

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


def fake_editor_command(input):
    return os.path.abspath("testing-tools/fake-editor") + " " + repr(input)


class SystestEnvironment(object):
    def __init__(self, testdir):
        self.testdir = testdir
        
    def deft(self, *args, **kwargs):
        env = {
            'PYTHONPATH': os.path.abspath("src"),
            'DEFT_EDITOR': fake_editor_command(kwargs.get('editor_input', 'description-not-important'))
        }
        
        return self.run(command=["deft"]+list(args), env_override=env)
    
    def run(self, command, env_override={}):
        path = search_path(os.path.abspath('python-dev/bin'),
                           os.path.abspath(os.getcwd()),
                           os.defpath)
        
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
        

def search_path(*paths):
    return os.pathsep.join(paths)


def tname():
    for frame in inspect.stack():
        methodname = frame[3]
        if methodname.startswith("test_"):
            return methodname
    
    raise ValueError, "no test method in call stack"


def fail(message):
    raise AssertionError(message)


def systest(f):
    @wraps(f)
    def run_test():
        testdir = os.path.join("output", "testing", "systest", f.__module__ + "." + f.func_name)
        ensure_empty_dir_exists(testdir)
        env = SystestEnvironment(testdir)
        f(env)
    
    return compose(istest, attr('systest'))(run_test)



def wip(f):
    @wraps(f)
    def run_test(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            raise SkipTest("WIP test failed: " + str(e))
        fail("test passed but marked as work in progress")
    
    return attr('wip')(run_test)
