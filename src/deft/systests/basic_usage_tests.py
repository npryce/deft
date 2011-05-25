
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
def test_can_create_with_initial_status():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "x", "--status", "initial-for-x")
    env.deft("create", "y", "--status", "initial-for-y")
    
    assert_that(env.deft("list", "--status", "initial-for-x").stdout_lines, equal_to(["x"]))
    assert_that(env.deft("status", "x").stdout.strip(), equal_to("initial-for-x"))

    assert_that(env.deft("list", "--status", "initial-for-y").stdout_lines, equal_to(["y"]))
    assert_that(env.deft("status", "y").stdout.strip(), equal_to("initial-for-y"))


@systest
def test_changing_status():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "x")
    env.deft("create", "y")
    env.deft("status", "x", "in-progress")
    
    assert_that(env.deft("list", "--status", "new").stdout_lines, equal_to(["y"]))
    assert_that(env.deft("list", "--status", "in-progress").stdout_lines, equal_to(["x"]))
    
    assert_that(env.deft("status", "x").stdout.strip(), equal_to("in-progress"))
    
    assert_that(env.deft("priority", "y").stdout.strip(), equal_to("1"),
                "priority of y increased now x moved to new status bucket")


@systest
def test_querying_status():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "a-feature")
    
    assert_that(env.deft("status", "a-feature").stdout.strip(), equal_to("new"))
    
    env.deft("status", "a-feature", "testing")
    
    assert_that(env.deft("status", "a-feature").stdout.strip(), equal_to("testing"))


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
def test_changing_priority():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    env.deft("create", "a")
    env.deft("create", "b")
    env.deft("create", "c")
    env.deft("create", "d")
    
    env.deft("priority", "d", "2")
    
    assert_that(env.deft("list", "--status", "new").stdout_lines, equal_to(["a", "d", "b", "c"]))
    assert_that(env.deft("priority", "a").stdout.strip(), equal_to("1"))
    assert_that(env.deft("priority", "b").stdout.strip(), equal_to("3"))
    assert_that(env.deft("priority", "c").stdout.strip(), equal_to("4"))
    assert_that(env.deft("priority", "d").stdout.strip(), equal_to("2"))

    

