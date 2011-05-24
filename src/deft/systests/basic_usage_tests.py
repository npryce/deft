
from deft.systests.support import SystestEnvironment, ProcessError, systest
from hamcrest import *


@systest
def test_basic_usage():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "x", "--description", "description of x")
    env.deft("create", "y", "--description", "description of y")
    
    assert_that(env.deft("list", "--status", "new").stdout_lines, equal_to(["x", "y"]))
    
    env.deft("purge", "x")
    
    assert_that(env.deft("list", "--status", "new").stdout_lines, equal_to(["y"]))


@systest
def test_changing_status():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "x")
    env.deft("create", "y")
    env.deft("status", "x", "in-progress")
    
    assert_that(env.deft("list", "--status", "new").stdout_lines, equal_to(["y"]))
    assert_that(env.deft("list", "--status", "in-progress").stdout_lines, equal_to(["x"]))


@systest
def test_querying_priority():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "x")
    env.deft("create", "y")
    env.deft("create", "z")
    
    assert_that(env.deft("list", "--status", "new").stdout_lines, equal_to(["x", "y", "z"]))
    
    assert_that(env.deft("priority", "x").stdout.strip(), equal_to("1"))
    assert_that(env.deft("priority", "y").stdout.strip(), equal_to("2"))
    assert_that(env.deft("priority", "z").stdout.strip(), equal_to("3"))
    

@systest
def test_querying_status():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "a-feature")
    
    status = env.deft("status", "a-feature").stdout.strip()
    assert status == "new"
    
    env.deft("status", "a-feature", "testing")
    
    status = env.deft("status", "a-feature").stdout.strip()
    assert status == "testing"

