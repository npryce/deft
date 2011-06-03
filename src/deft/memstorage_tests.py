

import os
from deft.memstorage import MemStorage
from deft.storage_tests import StorageContract
from hamcrest import *


class MemStorage_Test(StorageContract):
    def setup(self):
        self.testdir = "testdir"
        self.storage = self.create_storage(self.testdir)
    
    def create_storage(self, basedir):
        return MemStorage(basedir)
    
    def test_can_report_relative_path_for_realpath(self):
        assert_that(self.create_storage("/foo/bar").relpath("/foo/bar/x/y"), equal_to("x/y"))
        assert_that(self.create_storage("foo/bar").relpath("foo/bar/x/y"), equal_to("x/y"))
        assert_that(self.create_storage("foo").relpath("foo/x/y"), equal_to("x/y"))
        assert_that(self.create_storage("").relpath("x/y"), equal_to("x/y"))
        assert_that(self.create_storage(".").relpath("x/y"), equal_to("x/y"))
        
    
