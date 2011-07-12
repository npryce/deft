

import os
from deft.storage.memory import MemStorage, MemoryIO
from deft.storage.contract import TransientStorageContract, ReadOnlyStorageContract
from hamcrest import *
from nose.tools import raises


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
    
    
class MemStorage_ReadOnly_Test(ReadOnlyStorageContract):
    def __init__(self):
        self.testdir = "testdir"
        self.storage = self.create_storage()
    
    def create_storage(self, basedir=None):
        return MemStorage(self.testdir if basedir is None else basedir,
                          readonly=True)
    
    # Demonstrates switching to read/write mode
    def given_file(self, relpath, content="testing"):
        with self.storage.writeable:
            with self.storage.open(relpath, "w") as output:
                output.write(content)
    
    @raises(IOError)
    def test_will_not_open_files_for_writing_when_in_read_only_mode(self):
        self.storage.open("a/path", "w")
    
    @raises(IOError)
    def test_will_not_make_directories_when_in_read_only_mode(self):
        self.storage.makedirs("some/dirs")
    
    @raises(IOError)
    def test_will_not_delete_files_when_in_read_only_mode(self):
        self.given_file("a/file")
        
        self.storage.remove("a/file")
    
    @raises(IOError)
    def test_will_not_delete_nonexistent_files_when_in_read_only_mode(self):
        self.storage.remove("a/nonexistent/file")
    
    @raises(IOError)
    def test_will_not_rename_files_when_in_read_only_mode(self):
        self.given_file("a/file")
        
        self.storage.rename("a/file", "another/name")

    @raises(IOError)
    def test_will_not_rename_nonexistent_files_when_in_read_only_mode(self):
        self.storage.rename("a/nonexistent/file", "another/name")
