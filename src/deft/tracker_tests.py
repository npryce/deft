
from deft.tracker import FeatureTracker, default_config, PropertiesSuffix, UserError
from memstorage import MemStorage
from hamcrest import *


class FeatureTracker_Test:
    def setup(self):
        self.storage = MemStorage("basedir")
        self.tracker = FeatureTracker(default_config(datadir="tracker"), self.storage)
        
    def test_initially_contains_no_features(self):
        assert_that(list(self.tracker.all_features()), has_length(0))
    
    def test_reports_initial_status(self):
        tracker = FeatureTracker(default_config(initial_status="testing"), self.storage)
        assert_that(tracker.initial_status, equal_to("testing"))
        
    def test_default_initial_status_is_new(self):
        assert_that(self.tracker.initial_status, equal_to("new"))

    def test_can_create_new_features(self):
        new_feature = self.tracker.create(name="alice", status="pending")
        
        assert_that(new_feature.name, equal_to("alice"))
        assert_that(new_feature.status, equal_to("pending"))
    
    def test_new_features_have_default_initial_status_if_status_not_explicitly_specified(self):
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
        
        alice.priority = 3
        assert_priority_order("moved first to middle", bob, carol, alice, dave, eve)
        
        carol.priority = 1
        assert_priority_order("moved middle to first", carol, bob, alice, dave, eve)
        
        eve.priority = 1
        assert_priority_order("moved last to first", eve, carol, bob, alice, dave)
        
        bob.priority = 5
        assert_priority_order("moved middle to last", eve, carol, alice, dave, bob)
        
        eve.priority = 5
        assert_priority_order("moved first to last", carol, alice, dave, bob, eve)
        
        eve.priority = 3
        assert_priority_order("moved last to middle", carol, alice, eve, dave, bob)
        
        dave.priority = 2
        assert_priority_order("moved middle to middle", carol, dave, alice, eve, bob)
    
        
    def test_can_change_status(self):
        assert_status = self.assert_status
        
        alice = self.tracker.create(name="alice", status="odd")
        bob = self.tracker.create(name="bob", status="odd")
        carol = self.tracker.create(name="carol", status="odd")
        dave = self.tracker.create(name="dave", status="even")
        eve = self.tracker.create(name="eve", status="odd")
        
        alice.status = "female"
        assert_status("alice -> female",
                      female = [alice],
                      odd = [bob, carol, eve],
                      even = [dave])
        
        bob.status = "male"
        assert_status("bob -> male",
                      female = [alice],
                      male = [bob],
                      odd = [carol, eve],
                      even = [dave])
        
        carol.status = "female"
        assert_status("carol -> female",
                      female = [alice, carol],
                      male = [bob],
                      odd = [eve],
                      even = [dave])
        
        dave.status = "male"
        assert_status("dave -> male",
                      female = [alice, carol],
                      male = [bob, dave],
                      odd = [eve],
                      even = [])
        
        eve.status = "female"
        assert_status("eve -> female",
                      female = [alice, carol, eve],
                      male = [bob, dave],
                      odd = [],
                      even = [])
    
    def test_lists_all_statuses_in_alphabetical_order(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="U")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="T")
        eve = self.tracker.create(name="eve", status="S")
        
        assert_that(self.tracker.statuses, equal_to(["S", "T", "U"]))
        
    def test_does_not_list_empty_indices(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="U")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="T")
        eve = self.tracker.create(name="eve", status="S")
        
        bob.status = "V"
        
        assert_that(self.tracker.statuses, equal_to(["S", "T", "V"]))
        
    def test_an_unused_status_is_reported_as_empty(self):
        assert_status = self.assert_status
        
        assert_status("never used status", unused_status = [])
    
    def test_lists_names_of_all_features_in_order_of_status_then_priority(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="U")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="T")
        eve = self.tracker.create(name="eve", status="S")
        
        assert_that(list(self.tracker.all_features()), equal_to([alice, eve, carol, dave, bob]))
    
    def test_lists_names_of_features_with_given_status_in_priority_order(self):
        alice = self.tracker.create(name="alice", status="same")
        bob = self.tracker.create(name="bob", status="same")
        carol = self.tracker.create(name="carol", status="same")
        dave = self.tracker.create(name="dave", status="same")
        eve = self.tracker.create(name="eve", status="different")
        
        assert_that(list(self.tracker.features_with_status("same")), equal_to([alice, bob, carol, dave]))
    
    def test_can_create_feature_with_a_description(self):
        new_feature = self.tracker.create(name="new-feature", description="the description text")
        
        assert_that(new_feature.description, equal_to("the description text"))

    def test_can_create_feature_with_properties(self):
        new_feature = self.tracker.create(name="new-feature", properties={"a":"1", "b":"2"})
        
        assert_that(new_feature.properties, equal_to({"a":"1", "b":"2"}))
    
    def test_cannot_create_property_with_reserved_name(self):
        for name in ["status", "priority", "description"]:
            try:
                self.tracker.create(name="feature-for-"+name, properties={name: "y"})
                raise AssertionError("should have disallowed property named " + name)
            except UserError as e:
                assert_that(str(e), contains_string(name))
    
    def test_cannot_set_property_with_reserved_name(self):
        feature = self.tracker.create(name="x")
        for name in ["status", "priority", "description"]:
            try:
                feature.properties = {name: "y"}
                raise AssertionError("should have disallowed property named " + name)
            except UserError as e:
                assert_that(str(e), contains_string(name))
    
    
    def test_if_not_given_a_new_feature_has_an_empty_description(self):
        new_feature = self.tracker.create(name="new-feature")
        
        assert_that(new_feature.description, equal_to(""))
        
    def test_can_overwrite_the_description(self):
        new_feature = self.tracker.create(name="new-feature", description="the initial description")
        
        new_feature.description = "a new description"
        
        assert_that(new_feature.description, equal_to("a new description"))
    
    def test_can_overwrite_the_properties(self):
        new_feature = self.tracker.create(name="new-feature", properties={"a":"1", "b":"2"})
        
        new_feature.properties = {"a": "10", "b": "22"}
        
        assert_that(new_feature.properties, equal_to({"a": "10", "b": "22"}))
    
    def returns_a_copy_of_its_properties(self):
        new_feature = self.tracker.create(name="new-feature", properties={"a":"1", "b":"2"})
        
        new_feature.properties["1"] = "10"
        
        assert_that(new_feature.properties, equal_to({"a": "1", "b": "2"}))
        
    def test_can_report_filename_of_description(self):
        feature = self.tracker.create(name="bob")
        assert_that(feature.description_file, equal_to("basedir/tracker/features/bob.description"))
    
    def test_can_report_filename_of_properties(self):
        feature = self.tracker.create(name="carol")
        assert_that(feature.properties_file, equal_to("basedir/tracker/features/carol.properties.yaml"))
    
    def test_description_written_to_storage_immediately_when_feature_is_created(self):
        alice = self.tracker.create(name="alice", description="first-description")
        assert_that(self.storage.open("tracker/features/alice.description").read(), equal_to("first-description"))
        
    def test_description_written_to_storage_immediately_when_description_is_changed(self):
        alice = self.tracker.create(name="alice", description="first-description")
        alice.description = "second-description"
        assert_that(self.storage.open("tracker/features/alice.description").read(), equal_to("second-description"))
        
    def test_can_rename_a_feature(self):
        f = self.tracker.create(name="alice", description="alice-description", properties={"gender": "female"})
        self.tracker.save()
        
        original_status = f.status
        original_priority = f.priority
        original_description = f.description
        original_properties = f.properties
        
        f.name = "carol"
        
        assert_that(f.name, equal_to("carol"))
        assert_that(f.status, equal_to(original_status))
        assert_that(f.priority, equal_to(original_priority))
        assert_that(f.description, equal_to(original_description))
        assert_that(f.properties, equal_to(original_properties))
        
        try:
            self.tracker.feature_named("alice")
            raise AssertionError("should have raised UserError")
        except UserError:
            pass
        
        assert_that(self.tracker.feature_named("carol"), same_instance(f))
        
    def test_can_rename_a_feature_to_same_name(self):
        f = self.tracker.create(name="alice", description="alice-description", properties={"gender": "female"})
        self.tracker.save()
        
        original_status = f.status
        original_priority = f.priority
        original_description = f.description
        original_properties = f.properties
        
        f.name = "alice"
        
        assert_that(f.name, equal_to("alice"))
        assert_that(f.status, equal_to(original_status))
        assert_that(f.priority, equal_to(original_priority))
        assert_that(f.description, equal_to(original_description))
        assert_that(f.properties, equal_to(original_properties))
        
        assert_that(self.tracker.feature_named("alice"), same_instance(f))
    
    def test_cannot_rename_a_feature_to_existing_name(self):
        alice = self.tracker.create(name="alice")
        bob = self.tracker.create(name="bob")
        
        try:
            bob.name = "alice"
            raise AssertionError("should have failed")
        except UserError as expected:
            pass
        
    def test_purging_a_feature_removes_all_trace_of_it_from_tracker_and_storage(self):
        alice = self.tracker.create(name="alice", status="new", description="alice-description")
        alice.properties = {'a': 'some value'}
        
        self.tracker.save()
        
        assert_that(list(self.storage.list("tracker/features/alice.*")), is_not(equal_to([])))
        
        self.tracker.purge("alice")
        
        try:
            self.tracker.feature_named("alice")
            raise AssertionError("should have thrown UserError")
        except UserError as expected:
            pass
        
        self.tracker.save()
        
        assert_that(list(self.storage.list("tracker/alice.*")), equal_to([]))
        
        
        
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
        
        
