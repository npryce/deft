

import os
from deft.storage.memory import MemStorage, MemoryIO
from deft.storage.contract import TransientStorageContract
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


class MemStorage_Test(TransientStorageContract):
    def setup(self):
        self.testdir = "testdir"
        self.storage = self.create_storage()
    
    def create_storage(self, basedir=None):
        return MemStorage(self.testdir if basedir is None else basedir)
    
    def test_can_report_relative_path_for_realpath(self):
        assert_that(MemStorage("/foo/bar").relpath("/foo/bar/x/y"), equal_to("x/y"))
        assert_that(MemStorage("foo/bar").relpath("foo/bar/x/y"), equal_to("x/y"))
        assert_that(MemStorage("foo").relpath("foo/x/y"), equal_to("x/y"))
        assert_that(MemStorage("").relpath("x/y"), equal_to("x/y"))
        assert_that(MemStorage(".").relpath("x/y"), equal_to("x/y"))
        
    
