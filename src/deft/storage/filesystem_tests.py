
import os
from deft.formats import TextFormat, YamlFormat
from deft.storage.filesystem import FileStorage
from deft.storage.memory import MemStorage, MemoryIO
from deft.fileops import *
from deft.storage.contract import PersistentStorageContract
from hamcrest import *
from nose.plugins.attrib import attr


def path(p):
    return os.path.join(*p.split("/"))


@attr("fileio")
class FileStorage_Test(PersistentStorageContract):
    def setup(self):
        self.testdir = os.path.join("output", "testing", self.__class__.__name__.lower(), str(id(self)))
        ensure_empty_dir_exists(self.testdir)
        self.storage = self.create_storage()
    
    def create_storage(self, basedir=None):
        return FileStorage(self.testdir if basedir is None else basedir)
    
    # FileStorage-specific behaviour

    def test_files_are_created_on_disk_in_basedir(self):
        self.given_file("foo/bar", content="example-content")
        
        assert_that(os.path.exists(self._abspath("foo/bar")))
        assert_that(open(self._abspath("foo/bar"),"r").read(), equal_to("example-content"))
    
    def test_deletes_files_from_disk(self):
        self.given_file("example-file")
        self.storage.remove("example-file")
        
        assert_that(os.path.exists(self._abspath("example-file")), equal_to(False))
    
    def test_deletes_directory_trees_from_disk(self):
        self.given_file("example-dir/example-file")
        self.storage.remove("example-dir")
        
        assert_that(os.path.exists(self._abspath("example-dir/example-file")), equal_to(False))
        assert_that(os.path.exists(self._abspath("example-dir")), equal_to(False))
    
    def _abspath(self, p):
        return os.path.abspath(os.path.join(self.testdir, path(p)))
    

