
import inspect
import os
import shutil
from subprocess import Popen, PIPE, CalledProcessError


def run(command, cwd=os.path.curdir):
    process = Popen(command, 
                    stdin=PIPE, stdout=PIPE, stderr=PIPE, 
                    close_fds=True, 
                    cwd=cwd)
    (stdout, stderr) = process.communicate()
    
    if process.returncode != 0:
        error = str(command) + " returned status code " + str(process.returncode) + "\n" + \
                "stderr: " + stderr + "\n" + \
                "stdout: " + stdout + "\n"
        raise AssertionError(error)
    
    return stdout


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

Deft = os.path.abspath("deft")

def test_basic_usage():
    testdir = os.path.join("output", "testing", "systest", tname())
    ensure_empty_dir_exists(testdir)
    
    run([Deft, "init", "-d", "data"], cwd=testdir)
    idx = run([Deft, "create", "x", "--description", "a description"], cwd=testdir).strip()
    idy = run([Deft, "create", "y", "--description", "a description"], cwd=testdir).strip()
    
    output = run([Deft, "list", "--status", "new"], cwd=testdir)
    
    assert output == "%s x\n%s y\n"%(idx, idy)

