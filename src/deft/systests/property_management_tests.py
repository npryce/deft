
from StringIO import StringIO
import os
from hamcrest import *
from deft.systests.support import systest, wip, ProcessError
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
    
    assert_that(env.deft("properties", "feature-x", "--print", "x", "y").lines, equal_to(["1", "2"]))

@systest
def can_list_all_the_properties_of_a_feature(env):
    env.deft("init")
    env.deft("create", "feature-x")
    env.deft("properties", "feature-x", "--set", "name", "alice")
    env.deft("properties", "feature-x", "--set", "age", "30", "--set", "gender", "female")
    
    assert_that(env.deft("properties", "feature-x").yaml, equal_to(
            {"name": "alice", 
             "age": "30", 
             "gender": "female"}))

@systest
def prints_nothing_if_feature_has_no_properties(env):
    env.deft("init")
    env.deft("create", "feature-x")
    
    assert_that(env.deft("properties", "feature-x").stdout, equal_to(""))

@systest
def is_an_error_to_request_nonexistent_property_by_name(env):
    env.deft("init")
    env.deft("create", "feature-x")
    
    try:
        env.deft("properties", "feature-x", "--print", "pname")
    except ProcessError as e:
        assert_that(e.stderr, contains_string("feature-x does not have a property named 'pname'"))

@systest
def can_edit_the_properties_of_a_feature(env):
    env.deft("init")
    
    env.deft("create", "feature-x")
    
    env.deft("properties", "feature-x", "--edit",
             editor_input="foo: bar\ncount: '1'")
    
    assert_that(env.deft("properties", "feature-x").yaml, equal_to({"foo": "bar", "count": "1"}))


@systest
def can_print_the_name_of_the_properties_file(env):
    env.deft("init", "-d", "tracker")
    
    env.deft("create", "feature-x")
    
    assert_that(env.deft("properties", "--file", "feature-x").value, equal_to(
            env.abspath(os.path.join("tracker", "features", "feature-x.properties.yaml"))))

@systest
def can_remove_properties(env):
    env.deft("init")
    env.deft("create", "feature-x")
    env.deft("properties", "feature-x", "--set", "x", "1")
    env.deft("properties", "feature-x", "--set", "y", "2")
    
    env.deft("properties", "feature-x", "--remove", "x")
    
    assert_that(env.deft("properties", "feature-x").yaml, equal_to({"y": "2"}))

@systest
def can_set_properties_when_creating_a_feature(env):
    env.deft("init")
    env.deft("create", "alice", "--set", "gender", "female", "--set", "age", "30")
    
    assert_that(env.deft("properties", "alice", "-p", "gender").value, equal_to("female"))
    assert_that(env.deft("properties", "alice", "-p", "age").value, equal_to("30"))
    
@systest
def can_include_properties_when_listing_features(env):
    env.deft("init")
    env.deft("create", "alice", "--set", "hair", "red", "--set", "eyes", "blue")
    env.deft("create", "bob", "--set", "hair", "brown", "--set", "eyes", "brown")
    env.deft("create", "carol", "--set", "hair", "blonde", "--set", "eyes", "hazel")
    env.deft("create", "dave", "--set", "hair", "green", "--set", "eyes", "bloodshot")
    
    assert_that(env.deft("list", "--properties", "hair", "eyes").rows.cols(2,3,4),
                equal_to([["alice", "red", "blue"],
                          ["bob", "brown", "brown"],
                          ["carol", "blonde", "hazel"],
                          ["dave", "green", "bloodshot"]]))
                
