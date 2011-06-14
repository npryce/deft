
import deft.tracker
from deft.systests.support import InMemoryEnvironment, ProcessError, systest_in, systest, fail
from hamcrest import *


@systest
def cannot_initialise_tracker_multiple_times(env):
    env.deft("init")
    
    try:
        env.deft("init")
        fail("deft should have failed when initialising an already initialised tracker")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("already initialised"))


@systest_in(InMemoryEnvironment)
def cannot_configure_an_uninitialised_tracker(env):
    """
    Cannot run this test against the real disk because the project also
    contains a Deft tracker database to track it's own features!
    """
    
    try:
        env.deft("configure", "--initial-status", "foo")
        fail("deft should have failed when configuring an uninitialised tracker")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("not initialised"))


@systest
def cannot_create_a_feature_with_same_name_as_existing_feature(env):
    env.deft("init")
    
    env.deft("create", "new-feature-name")
    
    try:
        env.deft("create", "new-feature-name")
        fail("deft should have failed when creating a feature with a duplicate name")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("new-feature-name"))
        assert_that(e.stderr, contains_string("already exists"))
    

@systest
def cannot_manipulate_a_feature_that_does_not_exist(env):
    env.deft("init")
    
    try:
        env.deft("priority", "nonexistent-feature")
        fail("deft should have failed")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("no feature named nonexistent-feature"))


@systest
def refuses_to_work_with_tracker_that_has_incompatible_format_version(env):
    env.storage.save_yaml(".deft/config", {
            'format': '9999.9999',
            'datadir': '.deft/data'})
    
    try:
        env.deft("list")
        fail("deft should have failed when run against an incompatible tracker")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("incompatible tracker"))
        assert_that(e.stderr, contains_string("found data in format version 9999.9999"))
        assert_that(e.stderr, contains_string("requires data in format version " + deft.tracker.FormatVersion))
