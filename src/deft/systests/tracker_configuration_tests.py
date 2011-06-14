
from deft.systests.support import systest
from hamcrest import *


@systest
def test_can_initialise_tracker_with_default_status_for_new_features(env):
    env.deft("init", "--initial-status", "unverified")
    env.deft("create", "new-feature")
    
    assert_that(env.deft("status", "new-feature").stdout.strip(), equal_to("unverified"))


@systest
def test_can_configure_tracker_with_default_status_for_new_features(env):
    env.deft("init", "--initial-status", "oops-a-mistake")
    env.deft("configure", "--initial-status", "initial")
    env.deft("create", "new-feature")
    
    assert_that(env.deft("status", "new-feature").stdout.strip(), equal_to("initial"))
