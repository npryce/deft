
import os
from storage import FileStorage, Cache, TextFormat, YamlFormat
from deft.fileops import *
from deft.memstorage import MemStorage, MemoryIO
from hamcrest import *
from nose.tools import raises
from nose.plugins.attrib import attr


def path(p):
    return os.path.join(*p.split("/"))


class StorageContract:
    @attr("fileio")
    def test_content_of_written_files_can_be_read(self):
        with self.storage.open("foo.txt", "w") as output:
            output.write("testing!")
        
        with self.storage.open("foo.txt", "r") as input:
            written_content = input.read()
        
        assert_that(written_content, equal_to("testing!"))
    
        
    @attr("fileio")
    def test_written_files_exist(self):
        self._create_example_file("example.txt")
        
        assert_that(self.storage.exists("example.txt"), equal_to(True))
    
        
    @attr("fileio")
    def test_automagically_makes_parent_directories_when_writing_files(self):
        self._create_example_file("parent/subparent/example.txt")
    
        assert_that(self.storage.exists("parent"), equal_to(True))
        assert_that(self.storage.exists("parent/subparent"), equal_to(True))

        
    @attr("fileio")
    @raises(IOError)
    def test_raises_ioerror_if_file_opened_for_reading_does_not_exist(self):
        assert_that(self.storage.exists("does-not-exist"), equal_to(False))
        self.storage.open("does-not-exist")
        
        
    @attr("fileio")
    def test_can_delete_files(self):
        self._create_example_file("to-be-deleted")
        
        self.storage.remove("to-be-deleted")
        
        assert_that(self.storage.exists("to-be-deleted"), equal_to(False))
        
    
    @attr("fileio")
    def test_ignores_attempt_to_delete_nonexistent_file(self):
        assert_that(self.storage.exists("nonexistent-file"), equal_to(False))
        
        self.storage.remove("nonexistent-file")
        
        assert_that(self.storage.exists("nonexistent-file"), equal_to(False))
    
    
    @attr("fileio")
    def test_can_delete_directory_tree(self):
        self._create_example_file("parent/child/file1")
        self._create_example_file("parent/child/file2")
        
        self.storage.remove("parent/child")
        
        assert_that(self.storage.exists("parent/child"), equal_to(False))
        assert_that(self.storage.exists("parent/child/file1"), equal_to(False))
        assert_that(self.storage.exists("parent/child/file2"), equal_to(False))
        
        assert_that(self.storage.exists("parent"), equal_to(True))
    
    
    @attr("fileio")
    def test_ignores_attempt_to_remove_nonexistent_directory_tree(self):
        self._create_example_file("dir/file")
        
        assert_that(self.storage.exists("another-dir"), equal_to(False))
        
        self.storage.remove("another-dir")
        
        assert_that(self.storage.exists("another-dir"), equal_to(False))
    
    
    @attr("fileio")
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
        
        
    @attr("fileio")
    def test_can_report_real_path_for_relative_path(self):
        assert_that(self.create_storage("/foo/bar").abspath("x/y"), equal_to("/foo/bar/x/y"))
        assert_that(self.create_storage("foo/bar").abspath("x/y"), equal_to("foo/bar/x/y"))
        assert_that(self.create_storage("foo/bar/../baz/.").abspath("x/y"), equal_to("foo/baz/x/y"))
        
    def _create_example_file(self, relpath, content="testing"):
        with self.storage.open(relpath, "w") as output:
            output.write(content)



class FileStorage_Test(StorageContract):
    def setup(self):
        self.testdir = os.path.join("output", "testing", self.__class__.__name__.lower(), str(id(self)))
        ensure_empty_dir_exists(self.testdir)
        self.storage = self.create_storage(self.testdir)
    
    def create_storage(self, basedir):
        return FileStorage(basedir)
    
    # FileStorage-specific behaviour

    @attr("fileio")
    def test_files_are_created_on_disk_in_basedir(self):
        self._create_example_file("foo/bar", content="example-content")
        
        assert_that(os.path.exists(self._abspath("foo/bar")))
        assert_that(open(self._abspath("foo/bar"),"r").read(), equal_to("example-content"))
    
    @attr("fileio")
    def test_deletes_files_from_disk(self):
        self._create_example_file("example-file")
        self.storage.remove("example-file")
        
        assert_that(os.path.exists(self._abspath("example-file")), equal_to(False))
    
    @attr("fileio")
    def test_deletes_directory_trees_from_disk(self):
        self._create_example_file("example-dir/example-file")
        self.storage.remove("example-dir/example-file")
        
        assert_that(os.path.exists(self._abspath("example-file")), equal_to(False))
        
    def _abspath(self, p):
        return os.path.abspath(os.path.join(self.testdir, path(p)))
    




class Cache_Tests:
    def test_caches_files_from_backing_storage(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        text = "the quick brown fox"
        
        with storage.open("the/path", "w") as out:
            out.write(text)
        
        assert_that(cache.load("the/path", TextFormat), equal_to(text))
        assert_that(cache.load("the/path", TextFormat), equal_to(text))
        
        assert_that(storage.read_count("the/path"), equal_to(1))
    
        
    def test_saves_objects_only_when_flushed(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        cache.save("a", "a1", TextFormat)
        cache.save("b", "b1", TextFormat)
        
        assert_that(not storage.exists("a"))
        assert_that(not storage.exists("b"))
        
        cache.flush()
        
        assert_that(storage.open("a").read(), equal_to("a1"))
        assert_that(storage.open("b").read(), equal_to("b1"))
        
        cache.save("a", "a2", TextFormat)
        cache.save("b", "b2", TextFormat)
        
        assert_that(storage.open("a").read(), equal_to("a1"))
        assert_that(storage.open("b").read(), equal_to("b1"))
        
        cache.flush()
        
        assert_that(storage.open("a").read(), equal_to("a2"))
        assert_that(storage.open("b").read(), equal_to("b2"))

    
    def test_can_flush_a_single_file(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        cache.save("a", "a1", TextFormat)
        cache.save("b", "b1", TextFormat)
        
        cache.flush_file("a")
        
        assert_that(storage.open("a").read(), equal_to("a1"))
        assert_that(not storage.exists("b"))
        
        cache.flush_file("b")
        
        assert_that(storage.open("a").read(), equal_to("a1"))
        assert_that(storage.open("b").read(), equal_to("b1"))
        
        cache.save("a", "a2", TextFormat)
        cache.save("b", "b2", TextFormat)
        
        cache.flush_file("b")
        assert_that(storage.open("a").read(), equal_to("a1"))
        assert_that(storage.open("b").read(), equal_to("b2"))
    
    
    def test_query_for_existence_of_file_checks_filesystem_and_cache(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        cache.save("x", "x-content", TextFormat)
        with storage.open("y", "w") as y_output: 
            y_output.write("y-content")
        
        assert_that(cache.exists("x"))
        assert_that(cache.exists("y"))
        
    
    def test_can_bind_update_callback_to_path(self):
        "for use in the Observer pattern"
        
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        d = {'a':1}
        
        cache.save("d_path", d, YamlFormat)
        
        update_callback = cache.observer_for("d_path")
        
        d['b'] = 2
        update_callback()
        
        cache.flush()
        
        assert_that(storage.open("d_path").read(), equal_to("a: 1\nb: 2\n"))
    
    
    def test_can_remove_files_from_cache(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        cache.save("x-path", "x", TextFormat)
        cache.flush()
        
        cache.remove("x-path")
        
        assert_that(not cache.exists("x-path"))
        assert_that(storage.exists("x-path"))
    
    
    def test_removed_files_are_removed_from_storage_when_cache_is_flushed(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        cache.save("x-path", "x", TextFormat)
        cache.flush()
        
        cache.remove("x-path")
        cache.flush()
        
        assert_that(not cache.exists("x-path"))
        assert_that(not storage.exists("x-path"))
    
    def test_can_save_over_a_removed_file_before_flush(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)

        cache.save("x-path", "x", TextFormat)
        cache.flush()
        
        cache.remove("x-path")
        cache.save("x-path", "new-x", TextFormat)

        assert_that(cache.exists("x-path"))
        assert_that(storage.exists("x-path"))
        
        cache.flush()
        
        assert_that(cache.exists("x-path"))
        assert_that(storage.exists("x-path"))
        assert_that(storage.open("x-path").read(), equal_to("new-x"))
    
    @raises(ValueError)
    def test_marking_a_removed_path_as_dirty_is_an_error(self):
        storage = MemStorage("basedir")
        cache = Cache(storage)
        
        cache.save("x-path", "x", TextFormat)
        cache.flush()
        
        cache.remove("x-path")
        cache.mark_dirty("x-path")
