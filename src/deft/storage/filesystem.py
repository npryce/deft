
import os
import shutil
from glob import iglob


class FileStorage(object):
    def __init__(self, basedir):
        self.basedir = basedir
    
    def abspath(self, relpath):
        return os.path.normpath(os.path.join(self.basedir, relpath))
    
    def exists(self, relpath):
        return os.path.exists(self.abspath(relpath))
    
    def isdir(self, relpath):
        return os.path.isdir(self.abspath(relpath))
    
    def open(self, relpath, mode="r"):
        if mode == "w":
            self._ensure_parent_dir_exists(relpath)
        
        return open(self.abspath(relpath), mode)
    
    def rename(self, old_relpath, new_relpath):
        old_abspath = self.abspath(old_relpath)
        new_abspath = self.abspath(new_relpath)
        
        try:
            if not os.path.exists(old_abspath):
                raise IOError(old_abspath + " does not exist")
            if os.path.isdir(old_abspath):
                raise IOError(old_abspath + " is a directory")
            if os.path.exists(new_abspath):
                raise IOError(new_abspath + " already exists")
            
            os.renames(old_abspath, new_abspath)
        except OSError as e:
            raise IOError(e.strerror)
    
    def _ensure_parent_dir_exists(self, relpath):
        self.makedirs(os.path.dirname(relpath))
    
    def remove(self, relpath):
        path = self.abspath(relpath)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
    
    def list(self, relpattern):
        pattern = self.abspath(relpattern)
        return (os.path.relpath(match, start=self.basedir) for match in iglob(pattern))
    
    def makedirs(self, relpath):
        if relpath != "":
            dirpath = self.abspath(relpath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)


