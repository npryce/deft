
import os
from hamcrest import *
from deft.systests.support import SystestEnvironment, ProcessError, systest, fail, wip


@systest
def can_set_the_description_of_a_feature(env):
    env.deft("init")
    env.deft("create", "feature-x", "--description", "initial-description")
    
    env.deft("description", "feature-x", "new-description")
    
    assert_that(env.deft("description", "feature-x").value, equal_to("new-description"))


@systest
def can_edit_the_description_of_a_feature(env):
    env.deft("init")
    
    env.deft("create", "feature-x", "--description", "initial-description")
    
    env.deft("description", "--edit", "feature-x",
             editor_input="edited-description")
    
    assert_that(env.deft("description", "feature-x").value, equal_to("edited-description"))


@wip
@systest
def can_print_the_name_of_the_description_file(env):
    env.deft("init", "-d", "tracker")
    
    env.deft("create", "feature-x", "--description", "initial-description")
    
    env.deft("description", "--file", "feature-x")
    
    assert_that(env.deft("description", "feature-x").value, equal_to(
            os.path.join("tracker", "feature-x.description")))
