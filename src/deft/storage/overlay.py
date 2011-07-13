
import os
from functools import partial
from fnmatch import fnmatch
from deft.storage.memory import MemoryIO


def path_to_elts(relpath):
    return relpath.split(os.sep)

def elts_to_path(elts):
    return os.sep.join(elts)

def walk(relpath):
    elts = path_to_elts(relpath)
    curpath = elts[0]
    
    yield curpath
    
    for elt in elts[1:]:
        curpath = os.path.join(curpath, elt)
        yield curpath


class Removal(object):
    def __init__(self, relpath):
        self.relpath = relpath
    
    exists = False
    isdir = False
    
    def open(self, mode):
        self.fail()
    
    def fail(self):
        raise IOError(self.relpath + " does not exist")


class Addition(object):
    def __init__(self, overlay, relpath, data):
        self.overlay = overlay
        self.relpath = relpath
        self.data = data
    
    exists = True
    isdir = False
    
    def open(self, mode):
        if mode == "r":
            return MemoryIO(self.data)
        else:
            return MemoryIO(save_callback=partial(self.overlay._store, self.relpath))


class DirectoryAddition(object):
    def __init__(self, relpath):
        self.relpath = relpath
    
    exists = True
    isdir = True
    
    def open(self, mode):
        raise IOError(relpath + " is a directory")



class UnderlyingFile(object):
    def __init__(self, overlay, relpath):
        self.overlay = overlay
        self.underlay = overlay.underlay
        self.relpath = relpath
    
    @property
    def exists(self):
        return self.underlay.exists(self.relpath)
    
    @property
    def isdir(self):
        return self.underlay.isdir(self.relpath)
    
    def open(self, mode):
        if mode == "r":
            return self.underlay.open(self.relpath, mode)
        else:
            return MemoryIO(save_callback=partial(self.overlay._store, self.relpath))


class OverlayStorage(object):
    def __init__(self, underlay):
        self.underlay = underlay
        self._deltas = {}
    
    def abspath(self, relpath):
        return self.underlay.abspath(relpath)
    
    def exists(self, relpath):
        return self._ref(relpath).exists
    
    def isdir(self, relpath):
        return self._delta_for(relpath).isdir
    
    def remove(self, relpath):
        self._deltas[relpath] = Removal(relpath)
        
        subdirs_pattern = os.path.join(relpath, "*")
        for deltapath in self._deltas:
            if fnmatch(deltapath, subdirs_pattern):
                del self._deltas[deltapath]
    
    def rename(self, from_relpath, to_relpath):
        if not self.exists(from_relpath):
            raise IOError(from_relpath + " does not exist")
        
        if self.isdir(from_relpath):
            raise IOError(from_relpath + " is a directory")
        
        if self.exists(to_relpath):
            raise IOError(to_relpath + " already exists")
        
        self._ensure_parent_dir_exists(to_relpath)
        self._deltas[to_relpath] = self._delta_for(from_relpath)
        self.remove(from_relpath)
        
    def open(self, relpath, mode="r"):
        if mode == "w":
            self._ensure_parent_dir_exists(relpath)
        return self._delta_for(relpath).open(mode)
    
    def _ensure_parent_dir_exists(self, relpath):
        self.makedirs(os.path.dirname(relpath))
    
    def list(self, relpattern):
        underlay_matches = self.underlay.list(relpattern)
        overlay_matches = [relpath for relpath in self._deltas if fnmatch(relpath, relpattern)]
        
        all_matches = set(underlay_matches).union(set(overlay_matches))
        
        return [path for path in all_matches if self._ref(path).exists]
    
    def makedirs(self, relpath):
        for subpath in walk(relpath):
            d = self._delta_for(subpath)
            if not d.exists:
                self._deltas[subpath] = DirectoryAddition(subpath)
            elif not d.isdir:
                raise IOError("cannot create directory " + relpath + ", " + subpath + " is a file")
    
    def _ref(self, relpath):
        for subpath in walk(relpath):
            if not self._delta_for(subpath).exists:
                return Removal(subpath)
        return self._delta_for(relpath)
    
    def _delta_for(self, relpath):
        if relpath in self._deltas:
            return self._deltas[relpath]
        else:
            return UnderlyingFile(self, relpath)
    
    def _store(self, relpath, data):
        self._deltas[relpath] = Addition(self, relpath, data)
    
       
