
import inspect
import os
import shutil
from deft.indexing import Bucket
from deft.tracker import Feature
from hamcrest import *

class FakeTracker:
    def _mark_dirty(self, feature):
        pass

tracker = FakeTracker()

def make_features(n):
    return [make_feature(i) for i in xrange(0,n)]

def make_feature(i):
    return Feature(tracker=tracker, 
                   name=chr(ord('a')+i), 
                   priority=i+1, 
                   status="testing", 
                   description="")


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
        
        d = make_feature(99)
        
        bucket.append(d)
        assert_that(d.priority, equal_to(1))
    
        
    def test_inserting_a_feature_respects_its_current_priority_and_inserts_above_existing_feature_with_same_priority(self):
        a, b, c = make_features(3)
        bucket = Bucket([a,b,c])
        
        x = make_feature(0)
        x.priority = 2
        
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
