
from collections import Counter
from functools import wraps
from deft.formats import LinesFormat
from deft.tracker import (FeatureTracker, default_config, PropertiesSuffix, 
                          UserError, LostAndFoundStatus)
from deft.storage.memory import MemStorage
from deft.storage.filesystem_tests import path
from deft.warn import IgnoreWarnings, WarningRecorder, WarningRaiser
from hamcrest import *


def assert_status(description, tracker, status_buckets):
    for status in status_buckets:
        assert_priority_order(description, tracker, features=status_buckets[status], status=status)


def assert_priority_order(description, tracker, features, status=None):
    status = status or tracker.initial_status
    
    assert_that(list(tracker.features_with_status(status)), equal_to(list(features)), 
                description + ", order of " + status)
    
    for i in range(len(features)):
        expected_priority = i+1
        assert_that(features[i].priority, equal_to(expected_priority), 
                    "priority " + str(expected_priority) + " after " + description)


def assert_features_not_duplicated_in_indices(description, tracker):
    counts = Counter()
    for status in tracker.statuses:
        for f in tracker.features_with_status(status):
            counts[f.name] += 1
    
    for name in counts:
        assert_that(description + ", count for " + name, counts[name], equal_to(1))


class FeatureTracker_HappyPath_Tests:
    def setup(self):
        self.storage = MemStorage("basedir")
        self.tracker = FeatureTracker(config=default_config(datadir="tracker"), 
                                      storage=self.storage, 
                                      warning_listener=WarningRaiser(AssertionError))
    
    def test_initially_contains_no_features(self):
        assert_that(list(self.tracker.all_features()), has_length(0))
    
    def test_reports_initial_status(self):
        tracker = FeatureTracker(config=default_config(initial_status="testing"), 
                                 storage=self.storage, 
                                 warning_listener=IgnoreWarnings())
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
        alice = self.tracker.create(name="alice")
        bob = self.tracker.create(name="bob")
        carol = self.tracker.create(name="carol")
        dave = self.tracker.create(name="dave")
        eve = self.tracker.create(name="eve")
        
        alice.priority = 3
        assert_priority_order("moved first to middle", self.tracker, [bob, carol, alice, dave, eve])
        
        carol.priority = 1
        assert_priority_order("moved middle to first", self.tracker, [carol, bob, alice, dave, eve])
        
        eve.priority = 1
        assert_priority_order("moved last to first", self.tracker, [eve, carol, bob, alice, dave])
        
        bob.priority = 5
        assert_priority_order("moved middle to last", self.tracker, [eve, carol, alice, dave, bob])
        
        eve.priority = 5
        assert_priority_order("moved first to last", self.tracker, [carol, alice, dave, bob, eve])
        
        eve.priority = 3
        assert_priority_order("moved last to middle", self.tracker, [carol, alice, eve, dave, bob])
        
        dave.priority = 2
        assert_priority_order("moved middle to middle", self.tracker, [carol, dave, alice, eve, bob])
    
        
    def test_can_change_status(self):
        alice = self.tracker.create(name="alice", status="odd")
        bob = self.tracker.create(name="bob", status="odd")
        carol = self.tracker.create(name="carol", status="odd")
        dave = self.tracker.create(name="dave", status="even")
        eve = self.tracker.create(name="eve", status="odd")
        
        alice.status = "female"
        assert_status("alice -> female", self.tracker,
                      {"female": [alice],
                       "odd": [bob, carol, eve],
                       "even": [dave]})
        
        bob.status = "male"
        assert_status("bob -> male", self.tracker,
                      {"female": [alice],
                       "male": [bob],
                       "odd": [carol, eve],
                       "even": [dave]})
        
        carol.status = "female"
        assert_status("carol -> female", self.tracker,
                      {"female": [alice, carol],
                       "male": [bob],
                       "odd": [eve],
                       "even": [dave]})
        
        dave.status = "male"
        assert_status("dave -> male", self.tracker,
                      {"female": [alice, carol],
                       "male": [bob, dave],
                       "odd": [eve],
                       "even": []})
        
        eve.status = "female"
        assert_status("eve -> female", self.tracker,
                      {"female": [alice, carol, eve],
                       "male": [bob, dave],
                       "odd": [],
                       "even": []})
    
    def test_lists_all_statuses_in_alphabetical_order(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="U")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="T")
        eve = self.tracker.create(name="eve", status="S")
        
        assert_that(self.tracker.statuses, equal_to(["S", "T", "U"]))
        
    def test_does_not_list_empty_status_indices(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="U")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="T")
        eve = self.tracker.create(name="eve", status="S")
        
        bob.status = "V"
        
        assert_that(self.tracker.statuses, equal_to(["S", "T", "V"]))
        
    def test_an_unused_status_is_reported_as_empty(self):
        assert_status("never used status", self.tracker, {"unused_status": []})
    
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
        

    def test_can_bulk_change_status_of_all_features_with_the_same_status(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="S")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="U")
        
        self.tracker.bulk_change_status(from_status="S", to_status="T")
        
        assert_status("after bulk change", self.tracker,
                      {"S": [],
                       "T": [carol, alice, bob],
                       "U": [dave]})

    def test_can_bulk_change_to_same_status(self):
        alice = self.tracker.create(name="alice", status="S")
        bob = self.tracker.create(name="bob", status="S")
        carol = self.tracker.create(name="carol", status="T")
        dave = self.tracker.create(name="dave", status="U")
        
        self.tracker.bulk_change_status(from_status="S", to_status="S")
        
        assert_status("after bulk change", self.tracker,
                      {"S": [alice, bob],
                       "T": [carol],
                       "U": [dave]})
        
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

    def test_deletes_index_file_when_it_becomes_empty(self):
        alice = self.tracker.create(name="alice", status="testing")
        bob = self.tracker.create(name="bob", status="testing")
        carol = self.tracker.create(name="carol", status="testing")
        
        assert_that(self.storage.exists("tracker/status/testing.index"), 
                    "index file exists")
        
        alice.status = "another-status"
        bob.status = "another-status"
        carol.status = "another-status"
        
        assert_that(not self.storage.exists("tracker/status/testing.index"),
                    "index file should not exist after all entries have been removed")


    def test_deletes_index_file_when_it_becomes_by_purging_features(self):
        self.tracker.create(name="alice", status="testing")
        self.tracker.create(name="bob", status="testing")
        
        assert_that(self.storage.exists("tracker/status/testing.index"), 
                    "index file exists")
        
        self.tracker.purge("alice")
        self.tracker.purge("bob")
        
        assert_that(not self.storage.exists("tracker/status/testing.index"),
                    "index file should not exist after all entries have been removed")

        
    def test_asking_for_an_empty_index_does_not_create_an_empty_file(self):
        empty = self.tracker.features_with_status("testing")
        assert_that(empty, equal_to([]))
        
        assert_that(not self.storage.exists("tracker/status/testing.index"),
                    "should not have created an empty index file")

def ignoring_warnings(fn):
    @wraps(fn)
    def apply_context(*args, **kwargs):
        with warnings.catch_warnings(record=True):
            return fn(*args, **kwargs)
    return apply_context


class FeatureTracker_StorageRepair_Tests:
    """
    These tests monkey about with the underlying storage to simulate failed merges.
    """
    
    def setup(self):
        self.storage = MemStorage()
    
    def test_puts_features_that_are_not_in_any_status_index_into_the_lost_and_found_index(self):
        self.create_features({"testing": ["alice", "bob", "carol", "dave"]})
        self.corrupt_index("testing", delete_entry("bob"))
        tracker = self.create_tracker()
        
        repaired_feature = tracker.feature_named("bob")
            
        assert_that(repaired_feature in tracker.features_with_status(LostAndFoundStatus), 
                    LostAndFoundStatus + " status should include the repaired feature")
            
        assert_status("after repair", tracker,
                      {"testing": [tracker.feature_named("alice"),
                                   tracker.feature_named("carol"),
                                   tracker.feature_named("dave")],
                       "lost+found": [repaired_feature]})
    
    
    def test_persists_lost_and_found_index_when_orphaned_feature_is_repaired(self):
        self.test_puts_features_that_are_not_in_any_status_index_into_the_lost_and_found_index()
        
        # Should not need to repair the indices and so will not issue repair warnings
        tracker = self.create_tracker(warning_listener=WarningRaiser(AssertionError))
        
        assert_status("after repair", tracker,
                      {"testing": [tracker.feature_named("alice"),
                                   tracker.feature_named("carol"),
                                   tracker.feature_named("dave")],
                       "lost+found": [tracker.feature_named("bob")]})
 
    def test_saves_lost_and_found_index_when_multiple_orphaned_features_are_repaired(self):
        self.create_features({"testing": ["alice", "bob", "carol", "dave"]})
        self.corrupt_index("testing", delete_entry("bob"))
        self.corrupt_index("testing", delete_entry("carol"))
        self.create_tracker() # will repair the index
        
        
        tracker = self.create_tracker() # another tracker
        bob = tracker.feature_named("bob")
        carol = tracker.feature_named("carol")
        
        for repaired_feature in [bob, carol]:
            assert_that(repaired_feature in tracker.features_with_status(LostAndFoundStatus), 
                        LostAndFoundStatus + " status should include the repaired feature")

        assert_status("after repair", tracker,
                      {"testing": [tracker.feature_named("alice"),
                                   tracker.feature_named("dave")],
                       "lost+found": [bob, carol]})
   
    def test_issues_warning_when_repairing_feature_that_is_not_in_any_status_index(self):
        self.create_features({"testing": ["alice", "bob", "carol", "dave"]})
        self.corrupt_index("testing", delete_entry("bob"))
        
        warnings = WarningRecorder()
        tracker = self.create_tracker(warning_listener=warnings)
        
        assert_that(list(warnings), equal_to([
                    ("unindexed_feature", {"feature": tracker.feature_named("bob")})]))
        
    
    def test_removes_duplicated_entries_when_in_same_index(self):
        self.create_features({"testing": ["alice", "bob", "carol", "dave"]})
        self.corrupt_index("testing", insert_entry(3, "bob"))
        tracker = self.create_tracker()
        
        assert_features_not_duplicated_in_indices("after repair", tracker)
    

    def test_removes_duplicated_entries_when_in_different_indices(self):
        self.create_features({"s1": ["alice", "bob", "carol"],
                              "s2": ["dave", "eve"]})
        self.corrupt_index("s2", insert_entry(2, "bob"))
        tracker = self.create_tracker()
        
        assert_features_not_duplicated_in_indices("after repair", tracker)
        
        assert_status("tracker state after repair", tracker,
                      {"s1": [tracker.feature_named("alice"), 
                              tracker.feature_named("bob"), 
                              tracker.feature_named("carol")],
                       "s2": [tracker.feature_named("dave"), 
                              tracker.feature_named("eve")]})
        

    def test_persists_removal_of_duplicate_index_entries(self):
        self.test_removes_duplicated_entries_when_in_different_indices()
        
        # Should not need to repair the indices and so will not issue repair warnings
        self.create_tracker(warning_listener=WarningRaiser(AssertionError))
        
    
    def test_warns_when_removing_duplicate_index_entries(self):
        self.create_features({"s1": ["alice", "bob", "carol"],
                              "s2": ["dave", "eve"]})
        self.corrupt_index("s2", insert_entry(2, "bob"))
        
        warnings = WarningRecorder()
        tracker = self.create_tracker(warning_listener=warnings)
            
        assert_that(list(warnings), equal_to([
                    ("duplicate_entries", {"feature": tracker.feature_named("bob"), 
                                           "removed_from_status": "s2"})]))

    def test_filters_nonexistent_features_from_indices(self):
        self.create_features({"s1": ["alice", "bob"],
                              "s2": ["carol", "dave"]})
        self.corrupt_index("s2", insert_entry(2, "eve"))
        
        tracker = self.create_tracker()
        
        assert_status("after repair", tracker,
                      {"s1": [tracker.feature_named("alice"),
                              tracker.feature_named("bob")],
                       "s2": [tracker.feature_named("carol"),
                              tracker.feature_named("dave")]})
    
    def test_warns_if_index_contains_nonexistent_feature(self):
        self.create_features({"s1": ["alice", "bob"],
                              "s2": ["carol", "dave"]})
        self.corrupt_index("s2", insert_entry(2, "eve"))
        
        warnings = WarningRecorder()
        tracker = self.create_tracker(warning_listener=warnings)
        
        assert_that(list(warnings), equal_to([
                    ("unknown_feature", {"name": "eve", "status": "s2"})]))
        
    def test_persists_removal_of_nonexistent_features_from_indices(self):
        self.test_filters_nonexistent_features_from_indices()
        
        # Should not need to repair the indices and so will not issue repair warnings
        self.create_tracker(warning_listener=WarningRaiser(AssertionError))

    

    def create_tracker(self, warning_listener=None):
        return FeatureTracker(config=default_config(datadir="tracker"), 
                              storage=self.storage, 
                              warning_listener=warning_listener if warning_listener is not None else IgnoreWarnings())

    def create_features(self, names_by_status):
        tracker = self.create_tracker()
        for status in names_by_status:
            for name in names_by_status[status]:
                tracker.create(name=name, status=status)


    def corrupt_index(self, name, modifier):
        index_path = path("tracker/status/" + name + ".index")
        with self.storage.open(index_path) as input:
            index_entries = LinesFormat(list).load(input)

        modifier(index_entries)
    
        with self.storage.open(index_path, "w") as output:
            LinesFormat(list).save(index_entries, output)


def delete_entry_at(n):
    def modifier(seq):
        del seq[n]
    return modifier

def delete_entry(entry):
    def modifier(seq):
        seq.remove(entry)
    return modifier

def insert_entry(i, new_entry):
    def modifier(seq):
        seq.insert(i, new_entry)
    return modifier

