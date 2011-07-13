
import os
from deft.storage.overlay import OverlayStorage, walk
from deft.storage.memory import MemStorage
from deft.storage.contract import TransientStorageContract
from hamcrest import *
from nose.tools import raises



class Walk_Tests:
    def test_yields_paths_from_base_to_final(self):
        assert_that(list(walk("a/b/c")), equal_to(["a", "a/b", "a/b/c"]))
        assert_that(list(walk("a")), equal_to(["a"]))


class OverlayStorage_Tests(TransientStorageContract):
    def setup(self):
        self.testdir = "testdir"
        self.storage = self.create_storage()
    
    def create_storage(self, basedir=None):
        return OverlayStorage(MemStorage(self.testdir if basedir is None else basedir, readonly=True))

    def given_file(self, relpath, content="testing"):
        with self.storage.underlay.writeable as underlay:
            with underlay.open(relpath, "w") as output:
                output.write(content)
    
