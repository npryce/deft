
import inspect
import os
import shutil
from subprocess import Popen, PIPE, CalledProcessError
from nose.tools import nottest
from nose.plugins.attrib import attr
from deft.fileops import *

systest = attr('systest')
Deft = os.path.abspath("deft")


class ProcessResultParsing(object):
    @property
    def stdout_lines(self):
        return self.stdout.splitlines()
    
    @property
    def stderr_lines(self):
        return self.stderr.splitlines()


class ProcessError(Exception, ProcessResultParsing):
    def __init__(self, result):
        Exception.__init__(self, result.stderr)
        self.command = result.command
        self.status = result.status
        self.stdout = result.stdout
        self.stderr = result.stderr


class ProcessResult(ProcessResultParsing):
    def __init__(self, command, status, stdout, stderr):
        self.command = command
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
    

class SystestEnvironment(object):
    def __init__(self):
        self.testdir = os.path.join("output", "testing", "systest", tname())
        ensure_empty_dir_exists(self.testdir)
    
    def deft(self, *args):
        return self.run(Deft, *args)
    
    def run(self, *command):
        dev_bin = os.path.abspath('deft-dev/bin')
        
        process = Popen(command, 
                        stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                        close_fds=True, 
                        cwd=self.testdir,
                        env={'PATH': search_path(dev_bin, os.defpath)})
        
        (stdout, stderr) = process.communicate()
        
        result = ProcessResult(command, process.returncode, stdout, stderr)
        
        if result.status != 0:
            raise ProcessError(result)
        else:
            return result


def search_path(*paths):
    return os.pathsep.join(paths)


def tname():
    for frame in inspect.stack():
        methodname = frame[3]
        if methodname.startswith("test_"):
            return methodname
    
    raise ValueError, "no test method in call stack"


