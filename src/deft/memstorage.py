
import sys
from StringIO import StringIO
import os
from fnmatch import fnmatch
from storage import StorageFormats


class MemStorageIO(StringIO):
    def __init__(self, storage, relpath, content=""):
        StringIO.__init__(self, content)
        self.storage = storage
        self.relpath = relpath
    
    def close(self):
        self.storage.files[self.relpath] = self.getvalue()
        StringIO.close(self)
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class MemStorage(StorageFormats):
    def __init__(self, basedir):
        self.basedir = basedir
        self.files = {}
    
    def abspath(self, relpath):
        return os.path.normpath(os.path.join(self.basedir, relpath))
    
    def relpath(self, abspath):
        norm_abspath = os.path.normpath(abspath)
        norm_basedir = os.path.normpath(self.basedir)
        return os.path.relpath(norm_abspath, norm_basedir)
    
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
        return MemStorageIO(self, relpath, self.files[relpath])
    
    def _open_write(self, relpath):
        self.makedirs(os.path.dirname(relpath))
        return MemStorageIO(self, relpath)
    
    def remove(self, relpath):
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
        if relpath != "":
            self.makedirs(os.path.dirname(relpath))
            self.files[relpath] = None

