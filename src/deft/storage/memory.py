
import sys
from StringIO import StringIO
import os
from fnmatch import fnmatch
from contextlib import contextmanager


def read_only_save_callback(data):
    pass


class MemoryIO(StringIO):
    def __init__(self, content="", save_callback=read_only_save_callback):
        StringIO.__init__(self, content)
        self._save_callback = save_callback
    
    def close(self):
        self._save_callback(self.getvalue())
        StringIO.close(self)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()



class MemStorage(object):
    "Only suitable for storing small directory trees and small amounts of data"
    
    def __init__(self, basedir="basedir", readonly=False):
        self.basedir = basedir
        self.readonly = readonly
        self.files = {}
        self.read_counts = {}
    
    def abspath(self, relpath):
        return os.path.normpath(os.path.join(self.basedir, relpath))
    
    def relpath(self, abspath):
        norm_abspath = os.path.normpath(abspath)
        norm_basedir = os.path.normpath(self.basedir)
        return os.path.relpath(norm_abspath, norm_basedir)
    
    def isdir(self, relpath):
        # A hack-job: should model directories properly
        return len(self.list(os.path.join(relpath, "*"))) != 0
    
    def read_count(self, relpath):
        return self.read_counts.get(relpath, 0)
    
    def exists(self, relpath):
        return relpath in self.files 
    
    def open(self, relpath, mode="r"):
        if relpath in self.files and self.files[relpath] is None:
            raise IOError(relpath + " is a directory")
        
        if mode == "r":
            return self._open_read(relpath)
        elif mode == "w":
            return self._open_write(relpath)
        else:
            raise ValueError("mode must be 'r' or 'w', was: " + mode)
    
    def _open_read(self, relpath):
        if not self.exists(relpath):
            raise IOError(relpath + " does not exist")
        
        self.read_counts[relpath] = self.read_counts.get(relpath,0) + 1
        
        def read_only(data):
            pass
        
        return MemoryIO(content=self.files[relpath])
    
    def _open_write(self, relpath):
        self._check_can_write("write", relpath)
        
        def store_data(data):
            self.files[relpath] = data
        
        self.makedirs(os.path.dirname(relpath))
        
        return MemoryIO(save_callback=store_data)
    
    def rename(self, relpath, newpath):
        if not relpath in self.files:
            raise IOError(relpath + " does not exist")
        
        if newpath in self.files:
            raise IOError(newpath + " already exists")
        
        if self.isdir(relpath):
            raise IOError(relpath + " is a directory")
        
        data = self.files.pop(relpath)
        self.makedirs(os.path.dirname(newpath))
        self.files[newpath] = data
        
    def remove(self, relpath):
        self._check_can_write("remove", relpath)
        
        for subpath in self.list(os.path.join(relpath, "*")):
            self.files.pop(subpath, None)
        self.files.pop(relpath, None)
    
    def list(self, relpattern):
        part_patterns = relpattern.split(os.path.sep)
        
        def parts_match(parts):
            return len(parts) == len(part_patterns) \
                and all([fnmatch(*pair) for pair in zip(parts, part_patterns)])
        
        def relpath_matches(relpath):
            return parts_match(relpath.split(os.path.sep))
        
        return sorted(filter(relpath_matches, self.files.keys()))
    
    def makedirs(self, relpath):
        self._check_can_write("make directory", relpath)
        
        if relpath != "":
            self.makedirs(os.path.dirname(relpath))
            self.files[relpath] = None
    
    def _check_can_write(self, action, relpath):
        if self.readonly:
            raise IOError("cannot "+action+" "+relpath+": storage is in read-only mode")

    
    @property
    @contextmanager
    def writeable(self):
        self.readonly = False
        try:
            yield self
        finally:
            self.readonly = True
