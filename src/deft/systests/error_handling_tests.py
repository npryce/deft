
from deft.systests.support import SystestEnvironment, ProcessError, systest, fail
from hamcrest import *


@systest
def test_cannot_initialise_tracker_multiple_times():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    
    try:
        env.deft("init", "-d", "data")
        fail("deft should have failed when initialising an already initialised tracker")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("already initialised"))

@systest
def test_cannot_create_feature_with_same_name_as_existing_feature():
    env = SystestEnvironment()
    
    env.deft("init", "-d", "data")
    
    env.deft("create", "new-feature-name")
    
    try:
        env.deft("create", "new-feature-name")
        fail("deft should have failed when creating a feature with a duplicate name")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("new-feature-name"))
        assert_that(e.stderr, contains_string("already exists"))

