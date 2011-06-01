

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
