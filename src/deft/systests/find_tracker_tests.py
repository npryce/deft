
import os
from deft.systests.support import systest_in, DevEnvironment
from hamcrest import *


@systest_in(DevEnvironment)
def test_can_find_tracker_if_invoked_in_subdirectory_of_project(env):
    env.deft("init", "-d", "tracker")
    env.deft("create", "feature-a")
    
    subdir = os.path.join("x", "y")
    env.makedirs(subdir)
    
    env.deft("create", "feature-b",
             cwd=subdir)
    
    assert_that(env.deft("list").stdout, contains_string("feature-b"))
