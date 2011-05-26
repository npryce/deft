
from deft.systests.support import SystestEnvironment, ProcessError, systest
from hamcrest import *


@systest
def test_basic_usage(env):
    env.deft("init", "-d", "data")
    env.deft("create", "x", "--description", "description of x")
    env.deft("create", "y", "--description", "description of y")
    
    assert_that(env.deft("list", "--status", "new").rows, equal_to([
                ["new", "1", "x"],
                ["new", "2", "y"]]))
    
    env.deft("purge", "x")
    
    assert_that(env.deft("list", "--status", "new").rows, equal_to([
                ["new", "1", "y"]]))


@systest
def test_can_create_with_initial_status(env):
    env.deft("init", "-d", "data")
    env.deft("create", "x", "--status", "initial-for-x")
    env.deft("create", "y", "--status", "initial-for-y")
    
    assert_that(env.deft("list", "--status", "initial-for-x").rows, equal_to([
                ["initial-for-x", "1", "x"]]))
    assert_that(env.deft("status", "x").value, equal_to("initial-for-x"))
    
    assert_that(env.deft("list", "--status", "initial-for-y").rows, equal_to([
                ["initial-for-y", "1", "y"]]))
    assert_that(env.deft("status", "y").value, equal_to("initial-for-y"))


@systest
def test_changing_status(env):
    env.deft("init")
    env.deft("create", "x")
    env.deft("create", "y")
    env.deft("status", "x", "in-progress")
    
    assert_that(env.deft("list", "--status", "new").rows, equal_to([
                ["new", "1", "y"]]))
    assert_that(env.deft("list", "--status", "in-progress").rows, equal_to([
                ["in-progress", "1", "x"]]))
    
    assert_that(env.deft("status", "x").value, equal_to("in-progress"))
    
    assert_that(env.deft("priority", "y").value, equal_to("1"),
                "priority of y increased now x moved to new status bucket")


@systest
def test_querying_status(env):
    env.deft("init", "-d", "data")
    env.deft("create", "a-feature")
    
    assert_that(env.deft("status", "a-feature").value, equal_to("new"))
    
    env.deft("status", "a-feature", "testing")
    
    assert_that(env.deft("status", "a-feature").value, equal_to("testing"))


@systest
def test_querying_priority(env):
    env.deft("init", "-d", "data")
    env.deft("create", "x")
    env.deft("create", "y")
    env.deft("create", "z")
    
    assert_that(env.deft("list", "--status", "new").rows.cols(2), equal_to([
                ["x"], 
                ["y"], 
                ["z"]]))
    
    assert_that(env.deft("priority", "x").value, equal_to("1"))
    assert_that(env.deft("priority", "y").value, equal_to("2"))
    assert_that(env.deft("priority", "z").value, equal_to("3"))


@systest
def test_changing_priority(env):
    env.deft("init")
    env.deft("create", "a")
    env.deft("create", "b")
    env.deft("create", "c")
    env.deft("create", "d")
    
    env.deft("priority", "d", "2")
    
    assert_that(env.deft("list", "--status", "new").rows.cols(1,2), equal_to([
                ["1", "a"], 
                ["2", "d"], 
                ["3", "b"], 
                ["4", "c"]]))
    assert_that(env.deft("priority", "a").value, equal_to("1"))
    assert_that(env.deft("priority", "b").value, equal_to("3"))
    assert_that(env.deft("priority", "c").value, equal_to("4"))
    assert_that(env.deft("priority", "d").value, equal_to("2"))


@systest    
def test_purging_unwanted_features(env):
    env.deft("init")
    env.deft("create", "a")
    env.deft("create", "b")
    env.deft("create", "c")
    env.deft("create", "d")
    
    env.deft("purge", "b")
    
    assert_that(env.deft("list", "--status", "new").rows.cols(2), equal_to([["a"], ["c"], ["d"]]))
    assert_that(env.deft("priority", "c").value, equal_to("2"))
    assert_that(env.deft("priority", "d").value, equal_to("3"))
