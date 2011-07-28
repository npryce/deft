
import os
from datetime import date
from deft.formats import YamlFormat
from deft.storage.git import GitStorageHistory
from nose.plugins.attrib import attr
from hamcrest import *


def format_version(storage):
    with storage.open(".deft/config") as input:
        return YamlFormat.load(input)["format"]

@attr("fileio")
class GitStorageHistory_Tests:
    """
    Note: these tests run against the project's own Git repository.  Since that history should be
          immutable, the tests should be stable.  If that assumption turns out to be wrong, the test
          should create a Git repo and known history from scratch.
    """
    
    def test_can_lookup_storage_by_commit_sha1(self):
        history = GitStorageHistory(os.curdir)
        
        # Latest format
        storage1 = history["bd36b237cfce52b8ef3101fd08d301ac7efca773"]
        assert_that(format_version(storage1), equal_to("3.0"))
        assert_that(storage1.list("tracker/*"), equal_to(["tracker/features", "tracker/status"]))
        assert_that(len(storage1.list("tracker/features/*")), equal_to(44))
        
        # Old format
        storage2 = history["2c6ab3b049221978494f1927214375a07b8f2db2"]
        assert_that(format_version(storage2), equal_to("2.0"))
        assert_that(len(storage2.list("tracker/*")), equal_to(36))
    
    def test_can_index_commits_by_date(self):
        # Note: probably only works in London timezone. Fix this!
        history = GitStorageHistory(os.curdir)
        
        date_index = history.eod_revisions()
        
        # Note: there are several commits on these days.  The latest one should be returned
        assert_that(date_index[date(2011,07,22)], equal_to("304896b628e478cd58cece4934153a2d67f6e2f6"))
        assert_that(date_index[date(2011,05,29)], equal_to("286759e14b5a799d8d0b1a319cda74f4d9343d82"))
