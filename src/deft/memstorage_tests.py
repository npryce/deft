

import os
from deft.memstorage import MemStorage, MemoryIO
from deft.storage_tests import StorageContract
from hamcrest import *


class MemoryIO_Tests:
    def test_can_read_from_in_memory_string(self):
        with MemoryIO("the data") as io:
            contents = io.read()
    
        assert_that(contents, equal_to("the data"))
    
    def test_passes_written_data_to_callback_on_close(self):
        captured = []
        def capture(data):
            captured.append(data)
        
        with MemoryIO(save_callback=capture) as io:
            io.write("the")
            io.write(" ")
            io.write("written data")
        
        assert_that(captured[0], equal_to("the written data"))


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
        
    
