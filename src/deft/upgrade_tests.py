
from deft.tracker import UserError, ConfigFile, load_config_from_storage, save_config_to_storage
from deft.upgrade import Upgrader
from deft.storage.memory import MemStorage
from hamcrest import *


def mock_upgrade_to(version):
    def upgrader(storage, config):
        config["format"] = version
    
    return upgrader

def never_called(*args, **kwargs):
    raise AssertionError("should never be called")


def storage_with_config(config):
    storage = MemStorage("testing")
    save_config_to_storage(storage, config)
    return storage

def storage_with_format(format):
    return storage_with_config({"format": format})

def format_of(storage):
    return load_config_from_storage(storage)["format"]

class Upgrader_Tests:
    def test_upgrades_from_existing_format_to_target_format(self):
        storage = storage_with_format("1.0")
        
        upgrader = Upgrader(target="2.0", steps={
                "1.0": mock_upgrade_to("2.0")})
        
        upgrader.upgrade(storage)
        
        assert_that(format_of(storage), equal_to("2.0"))
    
    def test_applies_multiple_upgrade_steps_until_format_is_same_as_target(self):
        storage = storage_with_format("1.0")
        
        upgrader = Upgrader(target="4.0", steps={
                "1.0": mock_upgrade_to("2.0"),
                "2.0": mock_upgrade_to("3.0"),
                "3.0": mock_upgrade_to("4.0")})
        
        upgrader.upgrade(storage)
        
        assert_that(format_of(storage), equal_to("4.0"))
        
    def test_does_not_have_to_start_from_lowest_version(self):
        storage = storage_with_format("2.0")
        
        upgrader = Upgrader(target="4.0", steps={
                "1.0": mock_upgrade_to("2.0"),
                "2.0": mock_upgrade_to("3.0"),
                "3.0": mock_upgrade_to("4.0")})
        
        upgrader.upgrade(storage)
        
        assert_that(format_of(storage), equal_to("4.0"))

    def test_raises_error_if_run_against_version_higher_than_target(self):
        storage = storage_with_format("3.0")
        
        upgrader = Upgrader(target="2.0", steps={
                "1.0": never_called,
                "2.0": never_called})
        
        try:
            upgrader.upgrade(storage)
            raise AssertionError("should have raised an exception")
        except UserError as e:
            assert_that(str(e), contains_string("cannot migrate from version 3.0 to version 2.0"))
    
    def test_raises_error_if_no_upgrader_from_current_version(self):
        storage = storage_with_format("1.0")
        
        upgrader = Upgrader(target="4.0", steps={
                "2.0": never_called,
                "3.0": never_called})
        
        try:
            upgrader.upgrade(storage)
            raise AssertionError("should have raised an exception")
        except UserError as e:
            assert_that(str(e), contains_string("cannot migrate from version 1.0 to version 4.0"))
    
    def test_returns_true_if_has_performed_upgrade_actions(self):
        storage = storage_with_format("1.0")
        
        upgrader = Upgrader(target="2.0", steps={
                "1.0": mock_upgrade_to("2.0")})
        
        assert_that(upgrader.upgrade(storage), equal_to(True))
    
    def test_returns_false_if_already_at_target_version(self):
        storage = storage_with_format("2.0")
        
        upgrader = Upgrader(target="2.0", steps={
                "1.0": never_called})
        
        assert_that(upgrader.upgrade(storage), equal_to(False))
        
        
