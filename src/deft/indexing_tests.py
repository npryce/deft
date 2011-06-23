
from itertools import count
import inspect
import os
import shutil
from deft.indexing import Bucket, PriorityIndex
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
    
    def test_has_useful_repr(self):
        assert_that(repr(PriorityIndex(['alice', 'bob', 'carol'])), 
                    equal_to("PriorityIndex(['alice', 'bob', 'carol'])"))


class Bucket_Test:
    def test_stores_features_in_priority_order(self):
        feature_a, feature_b, feature_c, feature_d = make_features(4)
        
        bucket = Bucket([feature_b, feature_d, feature_c, feature_a])
        
        assert_that(bucket[0], same_instance(feature_a))
        assert_that(bucket[1], same_instance(feature_b))
        assert_that(bucket[2], same_instance(feature_c))
        assert_that(bucket[3], same_instance(feature_d))
    
    def test_reports_number_of_elements(self):
        assert_that(len(Bucket(make_features(0))), equal_to(0))
        assert_that(len(Bucket(make_features(1))), equal_to(1))
        assert_that(len(Bucket(make_features(4))), equal_to(4))
        assert_that(len(Bucket(make_features(10))), equal_to(10))
    
    def test_is_iterable(self):
        features = make_features(3)
        bucket = Bucket(features)
        
        iterated = []
        for f in bucket:
            iterated.append(f)
            
        assert_that(iterated, equal_to(features))
            
    
    def test_appending_a_feature_sets_its_priority_to_lowest_in_bucket(self):
        a, b, c = make_features(3)
        bucket = Bucket([a,b,c])
        
        d, e = make_features(2)
        
        bucket.append(d)
        assert_that(d.priority, equal_to(4))
        assert_that(bucket[3], same_instance(d))
        
        bucket.append(e)
        assert_that(e.priority, equal_to(5))
        assert_that(bucket[4], same_instance(e))
    
    def test_appending_a_feature_to_empty_bucket_sets_its_priority_to_1(self):
        bucket = Bucket([])
        
        d = fake_feature(priority=99)
        
        bucket.append(d)
        assert_that(d.priority, equal_to(1))
    
        
    def test_inserting_a_feature_respects_its_current_priority_and_inserts_above_existing_feature_with_same_priority(self):
        a, b, c = make_features(3)
        bucket = Bucket([a,b,c])
        
        x = fake_feature(priority=2)
        
        bucket.insert(x)
        
        assert_that(bucket[0], same_instance(a))
        assert_that(bucket[1], same_instance(x))
        assert_that(bucket[2], same_instance(b))
        assert_that(bucket[3], same_instance(c))
        
        assert_that(a.priority, equal_to(1))
        assert_that(x.priority, equal_to(2))
        assert_that(b.priority, equal_to(3))
        assert_that(c.priority, equal_to(4))


    def test_removing_a_feature_increases_priority_of_those_below_it(self):
        a, b, c, d, e  = make_features(5)
        bucket = Bucket([a, b, c, d, e])
        
        bucket.remove(c)
        
        assert_that(bucket[0], same_instance(a))
        assert_that(a.priority, equal_to(1))
        
        assert_that(bucket[1], same_instance(b))
        assert_that(b.priority, equal_to(2))
        
        assert_that(bucket[2], same_instance(d))
        assert_that(d.priority, equal_to(3))
        
        assert_that(bucket[3], same_instance(e))
        assert_that(e.priority, equal_to(4))
    

    def test_can_raise_the_priority_of_a_feature(self):
        a, b, c, d, e = make_features(5)
        bucket = Bucket([a, b, c, d, e])
        
        bucket.change_priority(d, 2)
        
        assert_that(list(bucket), equal_to([a,d,b,c,e]))
        
        assert_that(a.priority, equal_to(1))
        assert_that(d.priority, equal_to(2))
        assert_that(b.priority, equal_to(3))
        assert_that(c.priority, equal_to(4))
        assert_that(e.priority, equal_to(5))
        
    
    def test_can_lower_the_priority_of_a_feature(self):
        a, b, c, d, e = make_features(5)
        bucket = Bucket([a, b, c, d, e])
        
        bucket.change_priority(b, 4)
        
        assert_that(list(bucket), equal_to([a,c,d,b,e]))
        
        assert_that(a.priority, equal_to(1))
        assert_that(c.priority, equal_to(2))
        assert_that(d.priority, equal_to(3))
        assert_that(b.priority, equal_to(4))
        assert_that(e.priority, equal_to(5))
