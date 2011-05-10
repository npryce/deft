
import inspect
import os
import shutil
from subprocess import Popen, PIPE, CalledProcessError


Deft = os.path.abspath("deft")

class SystestEnvironment:
    def __init__(self):
        self.testdir = testdir = os.path.join("output", "testing", "systest", tname())
        ensure_empty_dir_exists(self.testdir)
    
    def deft(self, *args):
        return self.run(Deft, *args)
    
    def run(self, *command):
        process = Popen(command, 
                        stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                        close_fds=True, 
                        cwd=self.testdir)
        
        (stdout, stderr) = process.communicate()
        
        return ProcessResult(command, process.returncode, stdout, stderr)
        

class ProcessResult:
    def __init__(self, command, status, stdout, stderr):
        self.command = command
        self.status = status
        self.stdout = stdout
        self.stderr = stderr
    
    def succeeds(self):
        if self.status != 0:
            error = str(self.command) + " returned status code " + str(self.status) + "\n" + \
                    "stderr: " + self.stderr + "\n" + \
                    "stdout: " + self.stdout + "\n"
            raise AssertionError(error)
        else:
            return self
    
    def stdout0(self):
        self.succeeds()
        return self.stdout


def ensure_dir_exists(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def ensure_dir_not_exists(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)

def ensure_empty_dir_exists(dirpath):
    ensure_dir_not_exists(dirpath)
    ensure_dir_exists(dirpath)


def tname():
    for frame in inspect.stack():
        methodname = frame[3]
        if methodname.startswith("test_"):
            return methodname
    
    raise ValueError, "no test method in call stack"


def parse_feature_list(s):
    return [(line[0:32], line[33:]) for line in s.split("\n")[:-1]]


def test_basic_usage():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data").succeeds()
    idx = env.deft("create", "x", "--description", "a description").stdout0().strip()
    idy = env.deft("create", "y", "--description", "a description").stdout0().strip()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    assert features == [(idx, "x"), (idy, "y")]
    
    env.deft("close", idx).succeeds()
    
    features = parse_feature_list(env.deft("list", "--status", "new").stdout0())
    
    assert features == [(idy, "y")]


