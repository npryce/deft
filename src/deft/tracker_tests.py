
from deft.tracker import FeatureTracker, default_config
from memstorage import MemStorage
from hamcrest import *


class FeatureTracker_Test:
    def setup(self):
        self.storage = MemStorage()
        self.tracker = FeatureTracker(default_config(datadir="tracker"), self.storage)
        
    def test_initially_contains_no_features(self):
        assert_that(self.tracker.all_features(), has_length(0))
    
    def test_reports_initial_status(self):
        tracker = FeatureTracker(default_config(initial_status="testing"), self.storage)
        assert_that(tracker.initial_status, equal_to("testing"))
        
    def test_default_initial_status_is_new(self):
        assert_that(self.tracker.initial_status, equal_to("new"))

    def test_can_create_new_features(self):
        new_feature = self.tracker.create(name="alice", status="pending")
        
        assert_that(new_feature.name, equal_to("alice"))
        assert_that(new_feature.status, equal_to("pending"))
    
    def test_new_features_have_default_inititial_status_if_status_not_explicitly_specified(self):
        new_feature = self.tracker.create(name="alice")
        
        assert_that(new_feature.status, equal_to(self.tracker.initial_status))
    
    def test_new_features_with_same_status_are_assigned_priority_in_order_of_addition(self):
        new_a = self.tracker.create(name="new_a", status="new")
        new_b = self.tracker.create(name="new_b", status="new")
        pending_a = self.tracker.create(name="pending_a", status="pending")
        new_c = self.tracker.create(name="new_c", status="new")
        pending_b = self.tracker.create(name="pending_b", status="pending")
        
        assert_that(new_a.priority, equal_to(1))
        assert_that(new_b.priority, equal_to(2))
        assert_that(new_c.priority, equal_to(3))
        
        assert_that(pending_a.priority, equal_to(1))
        assert_that(pending_b.priority, equal_to(2))
    
    def test_can_change_the_priority_of_a_feature(self):
        assert_priority_order = self.assert_priority_order
        
        alice = self.tracker.create(name="alice")
        bob = self.tracker.create(name="bob")
        carol = self.tracker.create(name="carol")
        dave = self.tracker.create(name="dave")
        eve = self.tracker.create(name="eve")
        
        self.tracker.change_priority(alice, 3)
        assert_priority_order("moved first to middle", bob, carol, alice, dave, eve)
        
        self.tracker.change_priority(carol, 1)
        assert_priority_order("moved middle to first", carol, bob, alice, dave, eve)
        
        self.tracker.change_priority(eve, 1)
        assert_priority_order("moved last to first", eve, carol, bob, alice, dave)
        
        self.tracker.change_priority(bob, 5)
        assert_priority_order("moved middle to last", eve, carol, alice, dave, bob)
        
        self.tracker.change_priority(eve, 5)
        assert_priority_order("moved first to last", carol, alice, dave, bob, eve)
        
        self.tracker.change_priority(eve, 3)
        assert_priority_order("moved last to middle", carol, alice, eve, dave, bob)
        
        self.tracker.change_priority(dave, 2)
        assert_priority_order("moved middle to middle", carol, dave, alice, eve, bob)
    
        
    def test_can_change_status(self):
        assert_status = self.assert_status
        
        alice = self.tracker.create(name="alice", status="odd")
        bob = self.tracker.create(name="bob", status="odd")
        carol = self.tracker.create(name="carol", status="odd")
        dave = self.tracker.create(name="dave", status="even")
        eve = self.tracker.create(name="eve", status="odd")
        
        self.tracker.change_status(alice, "female")
        assert_status("alice -> female",
                      female = [alice],
                      odd = [bob, carol, eve],
                      even = [dave])
        
        self.tracker.change_status(bob, "male")
        assert_status("bob -> male",
                      female = [alice],
                      male = [bob],
                      odd = [carol, eve],
                      even = [dave])
        
        self.tracker.change_status(carol, "female")
        assert_status("carol -> female",
                      female = [alice, carol],
                      male = [bob],
                      odd = [eve],
                      even = [dave])
        
        self.tracker.change_status(dave, "male")
        assert_status("dave -> male",
                      female = [alice, carol],
                      male = [bob, dave],
                      odd = [eve],
                      even = [])
        
        self.tracker.change_status(eve, "female")
        assert_status("eve -> female",
                      female = [alice, carol, eve],
                      male = [bob, dave],
                      odd = [],
                      even = [])
    
    def test_an_unused_status_is_reported_as_empty(self):
        assert_status = self.assert_status
        
        assert_status("never used status", unused_status = [])
                      
    
    def test_lists_names_of_all_features_in_order_of_status_then_priority(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="U")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="T")
        eve = self.tracker.create(name="eve", status="S")
        
        assert_that(self.tracker.all_features(), equal_to([alice, eve, carol, dave, bob]))
    
    def test_lists_names_of_features_with_given_status_in_priority_order(self):
        alice = self.tracker.create(name="alice", status="same")
        bob = self.tracker.create(name="bob", status="same")
        carol = self.tracker.create(name="carol", status="same")
        dave = self.tracker.create(name="dave", status="same")
        eve = self.tracker.create(name="eve", status="different")
        
        assert_that(list(self.tracker.features_with_status("same")), equal_to([alice, bob, carol, dave]))
    
    def test_can_initialise_feature_with_a_description(self):
        new_feature = self.tracker.create(name="new-feature", description="the description text")
        
        assert_that(new_feature.open_description().read(), equal_to("the description text"))
    
    def test_if_not_given_a_new_feature_has_an_empty_description(self):
        new_feature = self.tracker.create(name="new-feature")
        
        assert_that(new_feature.open_description().read(), equal_to(""))
        
    def test_can_overwrite_the_description(self):
        new_feature = self.tracker.create(name="new-feature", description="the initial description")
        
        with new_feature.open_description("w") as out:
            out.write("a new description")
        
        assert_that(new_feature.open_description().read(), equal_to("a new description"))
    
    
    def assert_status(self, description, **kwargs):
        for status in kwargs:
            self.assert_priority_order(description, *kwargs[status], status=status)
    
    def assert_priority_order(self, description, *features, **kwargs):
        status = kwargs.get("status", self.tracker.initial_status)
        
        assert_that(list(self.tracker.features_with_status(status)), equal_to(list(features)), 
                    "order after " + description)
        
        for i in range(len(features)):
            expected_priority = i+1
            assert_that(features[i].priority, equal_to(expected_priority), 
                        "priority " + str(expected_priority) + " after " + description)
        
        
