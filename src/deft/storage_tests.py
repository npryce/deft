
import os
from storage import FileStorage, TextFormat, YamlFormat
from deft.fileops import *
from deft.memstorage import MemStorage, MemoryIO
from hamcrest import *
from nose.tools import raises
from nose.plugins.attrib import attr


def path(p):
    return os.path.join(*p.split("/"))


class StorageContract:
    def test_content_of_written_files_can_be_read(self):
        with self.storage.open("foo.txt", "w") as output:
            output.write("testing!")
        
        with self.storage.open("foo.txt", "r") as input:
            written_content = input.read()
        
        assert_that(written_content, equal_to("testing!"))
    
        
    def test_written_files_exist(self):
        self._create_example_file("example.txt")
        
        assert_that(self.storage.exists("example.txt"), equal_to(True))
    
        
    def test_automagically_makes_parent_directories_when_writing_files(self):
        self._create_example_file("parent/subparent/example.txt")
    
        assert_that(self.storage.exists("parent"), equal_to(True))
        assert_that(self.storage.exists("parent/subparent"), equal_to(True))

        
    @raises(IOError)
    def test_raises_ioerror_if_file_opened_for_reading_does_not_exist(self):
        assert_that(self.storage.exists("does-not-exist"), equal_to(False))
        self.storage.open("does-not-exist")
        
        
    def test_can_delete_files(self):
        self._create_example_file("to-be-deleted")
        
        self.storage.remove("to-be-deleted")
        
        assert_that(self.storage.exists("to-be-deleted"), equal_to(False))
        
    
    def test_ignores_attempt_to_delete_nonexistent_file(self):
        assert_that(self.storage.exists("nonexistent-file"), equal_to(False))
        
        self.storage.remove("nonexistent-file")
        
        assert_that(self.storage.exists("nonexistent-file"), equal_to(False))
    
    
    def test_can_delete_directory_tree(self):
        self._create_example_file("parent/child/file1")
        self._create_example_file("parent/child/file2")
        
        self.storage.remove("parent/child")
        
        assert_that(self.storage.exists("parent/child"), equal_to(False))
        assert_that(self.storage.exists("parent/child/file1"), equal_to(False))
        assert_that(self.storage.exists("parent/child/file2"), equal_to(False))
        
        assert_that(self.storage.exists("parent"), equal_to(True))
    
    
    def test_ignores_attempt_to_remove_nonexistent_directory_tree(self):
        self._create_example_file("dir/file")
        
        assert_that(self.storage.exists("another-dir"), equal_to(False))
        
        self.storage.remove("another-dir")
        
        assert_that(self.storage.exists("another-dir"), equal_to(False))
    
    
    def test_lists_files_that_match_glob_pattern(self):
        self._create_example_file("a/b1/1.txt")
        self._create_example_file("a/b1/2.txt")
        self._create_example_file("a/b1/3.mpg")
        self._create_example_file("a/b2/c")
        self._create_example_file("x/y")
        
        assert_that(sorted(self.storage.list("a/b1/*.txt")), equal_to(
                ["a/b1/1.txt","a/b1/2.txt"]))
        
        assert_that(sorted(self.storage.list("a/b*/*")), equal_to(
                ["a/b1/1.txt","a/b1/2.txt","a/b1/3.mpg","a/b2/c"]))
        
        assert_that(sorted(self.storage.list("*")), equal_to(["a", "x"]))
        
        assert_that(list(self.storage.list("a/zzz*")), equal_to([]))
        assert_that(list(self.storage.list("zzz/*")), equal_to([]))
    
    def test_can_rename_files(self):
        self._create_example_file("x", content="x-contents")
        
        self.storage.rename("x", "y")
        
        assert_that(not self.storage.exists("x"))
        assert_that(self.storage.exists("y"))
        assert_that(self.storage.open("y").read(), equal_to("x-contents"))
        
    def test_can_rename_files_to_new_directory(self):
        self._create_example_file("parent/x", content="x-contents")
        
        self.storage.rename("parent/x", "basedir/y")
        
        assert_that(not self.storage.exists("parent/x"))
        assert_that(self.storage.exists("basedir/y"))
        assert_that(self.storage.open("basedir/y").read(), equal_to("x-contents"))
        
    @raises(IOError)
    def test_cannot_rename_nonexistent_files(self):
        self.storage.rename("file/that/does/not/exist", "irrelevant")
    
    @raises(IOError)
    def test_cannot_rename_file_over_existing_file(self):
        self._create_example_file("x")
        self._create_example_file("y")
        
        self.storage.rename("x", "y")
    
    def test_can_report_real_path_for_relative_path(self):
        assert_that(self.create_storage("/foo/bar").abspath("x/y"), equal_to("/foo/bar/x/y"))
        assert_that(self.create_storage("foo/bar").abspath("x/y"), equal_to("foo/bar/x/y"))
        assert_that(self.create_storage("foo/bar/../baz/.").abspath("x/y"), equal_to("foo/baz/x/y"))
        
    def _create_example_file(self, relpath, content="testing"):
        with self.storage.open(relpath, "w") as output:
            output.write(content)



@attr("fileio")
class FileStorage_Test(StorageContract):
    def setup(self):
        self.testdir = os.path.join("output", "testing", self.__class__.__name__.lower(), str(id(self)))
        ensure_empty_dir_exists(self.testdir)
        self.storage = self.create_storage(self.testdir)
    
    def create_storage(self, basedir):
        return FileStorage(basedir)
    
    # FileStorage-specific behaviour

    def test_files_are_created_on_disk_in_basedir(self):
        self._create_example_file("foo/bar", content="example-content")
        
        assert_that(os.path.exists(self._abspath("foo/bar")))
        assert_that(open(self._abspath("foo/bar"),"r").read(), equal_to("example-content"))
    
    def test_deletes_files_from_disk(self):
        self._create_example_file("example-file")
        self.storage.remove("example-file")
        
        assert_that(os.path.exists(self._abspath("example-file")), equal_to(False))
    
    def test_deletes_directory_trees_from_disk(self):
        self._create_example_file("example-dir/example-file")
        self.storage.remove("example-dir/example-file")
        
        assert_that(os.path.exists(self._abspath("example-file")), equal_to(False))
        
    def _abspath(self, p):
        return os.path.abspath(os.path.join(self.testdir, path(p)))
    

