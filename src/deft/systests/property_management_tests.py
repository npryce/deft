
from StringIO import StringIO
import os
from hamcrest import *
from deft.systests.support import systest, wip
from deft.storage import YamlFormat


@systest
def can_set_and_get_a_property_of_a_feature(env):
    env.deft("init")
    env.deft("create", "feature-x")
    env.deft("properties", "feature-x", "--set", "x", "1")
    env.deft("properties", "feature-x", "--set", "y", "2")
    
    assert_that(env.deft("properties", "feature-x", "--print", "x").value, equal_to("1"))
    assert_that(env.deft("properties", "feature-x", "--print", "y").value, equal_to("2"))

@systest
def can_query_multiple_properties_of_a_feature(env):
    env.deft("init")
    env.deft("create", "feature-x")
    env.deft("properties", "feature-x", "--set", "x", "1")
    env.deft("properties", "feature-x", "--set", "y", "2")
    
    assert_that(env.deft("properties", "feature-x", "--print", "x", "y").value, equal_to("1 2"))


@systest
def can_list_all_the_properties_of_a_feature(env):
    env.deft("init")
    env.deft("create", "feature-x")
    env.deft("properties", "feature-x", "--set", "name", "alice")
    env.deft("properties", "feature-x", "--set", "age", "30", "--set", "gender", "female")
    
    assert_that(env.deft("properties", "feature-x").yaml, equal_to(
            {"name": "alice", 
             "age": 30, 
             "gender": "female"}))
    

@systest
def can_edit_the_properties_of_a_feature(env):
    env.deft("init")
    
    env.deft("create", "feature-x")
    
    env.deft("properties", "feature-x", "--edit",
             editor_input="foo: bar\ncount: 1")
    
    assert_that(env.deft("properties", "feature-x").yaml, equal_to({"foo": "bar", "count": 1}))


@systest
def can_print_the_name_of_the_properties_file(env):
    env.deft("init", "-d", "tracker")
    
    env.deft("create", "feature-x")
    
    assert_that(env.deft("properties", "--file", "feature-x").value, equal_to(
            env.abspath(os.path.join("tracker", "feature-x.properties.yaml"))))
