

from properties import Properties
from hamcrest import *


class Properties_Tests:
    def test_can_be_initialised_empty(self):
        p = Properties()
        
        assert_that(not p)
    
    def test_can_be_initialised_from_an_existing_mapping(self):
        p = Properties({"foo": "bar", "num": 10})
        
        assert_that(p["foo"], equal_to("bar"))
        assert_that(p["num"], equal_to(10))
    
    def test_can_be_initialised_from_keyword_arguments(self):
        p = Properties(foo="bar", num=10)
        
        assert_that(p["foo"], equal_to("bar"))
        assert_that(p["num"], equal_to(10))
    
    def test_can_set_and_get_properties(self):
        p = Properties()
        
        p["foo"] = "bar"
        p["num"] = 10
        
        assert_that(p["foo"], equal_to("bar"))
        assert_that(p["num"], equal_to(10))
    
    def test_can_list_properties(self):
        p = Properties()
        
        p["alice"] = 1
        p["bob"] = 2
        p["carol"] = 3
        p["dave"] = 4
        p["eve"] = 5
        
        assert_that(set(p.keys()), equal_to(set(["alice", "bob", "carol", "dave", "eve"])))
    
    def test_can_append_to_property(self):
        p = Properties()
        
        p["tags"] = ["alice", "bob"]
        
        p.append("tags", "carol")
        
        assert_that(p["tags"], equal_to(["alice", "bob", "carol"]))
    
    def test_appending_to_scalar_property_turns_it_into_a_vector(self):
        p = Properties()
        
        p["tags"] = "alice"
        p.append("tags", "bob")
        
        assert_that(p["tags"], equal_to(["alice", "bob"]))
    
    def test_appending_to_new_property_turns_it_into_a_scalar(self):
        p = Properties()
        
        p.append("tags", "alice")
        
        assert_that(p["tags"], equal_to("alice"))
    
    def test_can_remove_element_from_list_property(self):
        p = Properties()
        
        p["tags"] = ["alice", "bob", "carol", "dave"]
        
        p.remove("tags", "bob")
        
        assert_that(p["tags"], equal_to(["alice", "carol", "dave"]))
        
        p.remove("tags", "alice")
        
        assert_that(p["tags"], equal_to(["carol", "dave"]))

    def test_removing_scalar_element_deletes_property(self):
        p = Properties()
        
        p["tags"] = "alice"
        
        p.remove("tags", "alice")
        
        assert_that("tags" not in p)
    
    def test_removing_penultimate_element_turns_property_to_a_scalar(self):
        p = Properties()
        
        p["tags"] = ["alice", "bob"]
        
        p.remove("tags", "bob")
        
        assert_that(p["tags"], equal_to("alice"))
    
    def test_removing_from_nonexistent_property_has_no_effect(self):
        p = Properties()
        
        p.remove("tags", "bob")
        
        assert_that("tags" not in p)
