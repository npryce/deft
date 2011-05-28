
from deft.systests.support import SystestEnvironment, ProcessError, systest, wip
from hamcrest import *


@systest
def can_create_new_features(env):
    env.deft("init", "-d", "data")
    env.deft("create", "x", "--description", "description of x")
    env.deft("create", "y", "--description", "description of y")
    
    assert_that(env.deft("list", "--status", "new").rows, equal_to([
                ["new", "1", "x"],
                ["new", "2", "y"]]))


@systest
def can_create_with_initial_status(env):
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
def can_list_all_issues_ordered_by_status_then_priority(env):
    env.deft("init")
    env.deft("create", "feature-1", "--status", "pending")
    env.deft("create", "feature-2", "--status", "pending")
    env.deft("create", "feature-3", "--status", "working")
    env.deft("create", "feature-4", "--status", "working")
    env.deft("create", "feature-5", "--status", "complete")
    env.deft("create", "feature-6", "--status", "complete")
    
    assert_that(env.deft("list").rows, equal_to([
                ["complete", "1", "feature-5"],
                ["complete", "2", "feature-6"],
                ["pending", "1", "feature-1"],
                ["pending", "2", "feature-2"],
                ["working", "1", "feature-3"],
                ["working", "2", "feature-4"]]))

@systest
def can_list_issues_in_multiple_statuses_in_order_that_statuses_are_given_then_by_priority(env):
    env.deft("init")
    env.deft("create", "feature-1", "--status", "pending")
    env.deft("create", "feature-2", "--status", "pending")
    env.deft("create", "feature-3", "--status", "working")
    env.deft("create", "feature-4", "--status", "working")
    env.deft("create", "feature-5", "--status", "complete")
    env.deft("create", "feature-6", "--status", "complete")
    
    assert_that(env.deft("list", "--status", "pending", "working", "complete").rows, equal_to([
                ["pending", "1", "feature-1"],
                ["pending", "2", "feature-2"],
                ["working", "1", "feature-3"],
                ["working", "2", "feature-4"],
                ["complete", "1", "feature-5"],
                ["complete", "2", "feature-6"]]))
    
    assert_that(env.deft("list", "-s", "working", "pending").rows, equal_to([
                ["working", "1", "feature-3"],
                ["working", "2", "feature-4"],
                ["pending", "1", "feature-1"],
                ["pending", "2", "feature-2"]]))

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
