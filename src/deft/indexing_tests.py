
from itertools import count
import inspect
import os
import shutil
from deft.indexing import PriorityIndex
from deft.tracker import Feature
from deft.fake_tracker import make_features, fake_feature
from hamcrest import *
from nose.tools import raises


    
def assert_feature_priorities(index, *feature_names):
    for (name, priority) in zip(feature_names, count(1)):
        assert_that(index.priority_of_feature(name), equal_to(priority),
                    "priority of " + name + " should be " + str(priority))
        assert_that(index.feature_with_priority(priority), equal_to(name),
                    "feature with priority " + str(priority) + " should be " + name)
    
    assert_that(list(index), equal_to(list(feature_names)))


class PriorityIndex_Test:
    def test_indexes_features_by_priority(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave", "eve"])
        
        assert_that(index.feature_with_priority(1), equal_to("alice"))
        assert_that(index.feature_with_priority(2), equal_to("bob"))
        assert_that(index.feature_with_priority(3), equal_to("carol"))
        assert_that(index.feature_with_priority(4), equal_to("dave"))
        assert_that(index.feature_with_priority(5), equal_to("eve"))
    
    def test_indexes_priorities_by_feature(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave", "eve"])
        
        assert_that(index.priority_of_feature("alice"), equal_to(1))
        assert_that(index.priority_of_feature("bob"), equal_to(2))
        assert_that(index.priority_of_feature("carol"), equal_to(3))
        assert_that(index.priority_of_feature("dave"), equal_to(4))
        assert_that(index.priority_of_feature("eve"), equal_to(5))
    
    def test_can_iterate_over_feature_names_in_priority_order(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave", "eve"])

        assert_that(list(index), equal_to(["alice", "bob", "carol", "dave", "eve"]))
    
    def test_can_append_features(self):
        index = PriorityIndex(["alice", "bob"])
        
        index.append("carol")
        assert_feature_priorities(index, "alice", "bob", "carol")
        
        index.append("dave")
        assert_feature_priorities(index, "alice", "bob", "carol", "dave")
        
    def test_can_remove_first_feature(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        index.remove("alice")
        
        assert_feature_priorities(index, "bob", "carol", "dave")
        
    def test_can_remove_middle_feature(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        index.remove("bob")
        
        assert_feature_priorities(index, "alice", "carol", "dave")
        
    def test_can_remove_last_feature(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        index.remove("dave")
        
        assert_feature_priorities(index, "alice", "bob", "carol")

    def test_can_append_after_removing(self):
        index = PriorityIndex(["alice", "bob", "carol"])
        
        index.remove("bob")
        index.append("dave")
        
        assert_feature_priorities(index, "alice", "carol", "dave")
        
    def test_can_insert_features_at_front(self):
        index = PriorityIndex(["alice", "bob", "carol"])
        
        index.insert("eve", 1)
        
        assert_feature_priorities(index, "eve", "alice", "bob", "carol")
        
    def test_can_insert_features_in_middle(self):
        index = PriorityIndex(["alice", "bob", "carol"])
        
        index.insert("eve", 3)
        
        assert_feature_priorities(index, "alice", "bob", "eve", "carol")
        
    def test_can_insert_features_in_middle(self):
        index = PriorityIndex(["alice", "bob", "carol"])
        
        index.insert("eve", 4)
        
        assert_feature_priorities(index, "alice", "bob", "carol", "eve")
        
    def test_limits_priorities_to_priority_one_on_insert(self):
        index = PriorityIndex(["alice", "bob", "carol"])
        
        index.insert("eve", 0)
        
        assert_feature_priorities(index, "eve", "alice", "bob", "carol")

    def test_limits_priorities_to_lowest_priority_on_insert(self):
        index = PriorityIndex(["alice", "bob", "carol"])
        
        index.insert("eve", 5)
        
        assert_feature_priorities(index, "alice", "bob", "carol", "eve")
    
    def test_can_move_feature_from_bottom_to_top(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.change_priority("dave", 1)
        
        assert_feature_priorities(index, "dave", "alice", "bob", "carol")

    def test_can_move_feature_from_top_to_bottom(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.change_priority("alice", 4)
        
        assert_feature_priorities(index, "bob", "carol", "dave", "alice")
    
    def test_can_move_feature_from_middle_to_top(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.change_priority("bob", 1)
        
        assert_feature_priorities(index, "bob", "alice", "carol", "dave")
    
    def test_can_move_feature_from_middle_to_bottom(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.change_priority("bob", 4)
        
        assert_feature_priorities(index, "alice", "carol", "dave", "bob")
        
    def test_can_move_feature_up_in_the_middle(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.change_priority("carol", 2)
        
        assert_feature_priorities(index, "alice", "carol", "bob", "dave")
        
    def test_can_move_feature_down_in_the_middle(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.change_priority("bob", 3)
        
        assert_feature_priorities(index, "alice", "carol", "bob", "dave")
        
    def test_moving_feature_to_same_priority_has_no_effect(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.change_priority("bob", 2)
        
        assert_feature_priorities(index, "alice", "bob", "carol", "dave")
    
    def test_can_rename_feature(self):
        index = PriorityIndex(["alice", "bob", "carol", "dave"])
        
        index.rename("bob", "robert")
        
        assert_feature_priorities(index, "alice", "robert", "carol", "dave")

    def test_has_useful_repr(self):
        assert_that(repr(PriorityIndex(['alice', 'bob', 'carol'])), 
                    equal_to("PriorityIndex(['alice', 'bob', 'carol'])"))

