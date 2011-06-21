
from functools import partial
import os
import shutil
from glob import iglob
import yaml


class StorageFormats(object):
    def save_yaml(self, relpath, obj):
        with self.open(relpath, "w") as output:
            yaml.safe_dump(obj, output, default_flow_style=False)
    
    def load_yaml(self, relpath):
        with self.open(relpath) as input:
            return yaml.safe_load(input)
    
    def save_text(self, relpath, text):
        with self.open(relpath, "w") as output:
            output.write(text)
            
    def load_text(self, relpath):
        with self.open(relpath) as input:
            return input.read()


class FileStorage(StorageFormats):
    def __init__(self, basedir):
        self.basedir = basedir
    
    def abspath(self, relpath):
        return os.path.normpath(os.path.join(self.basedir, relpath))
    
    def exists(self, relpath):
        return os.path.exists(self.abspath(relpath))
    
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



class Cache(object):
    def __init__(self, storage):
        self.storage = storage
        self._cached = {}
        self._removed = set()
        self._dirty = set()
    
    def exists(self, path):
        return path in self._cached or (path not in self._removed and self.storage.exists(path))
        
    def load(self, path, format):
        if path in self._cached:
            return self._cached[path][0]
        else:
            with self.storage.open(path, "r") as input:
                loaded_object = format.load(input)
                self._cache(path, loaded_object, format)
                return loaded_object
    
    def save(self, path, obj, format):
        self._cache(path, obj, format)
        self._removed.discard(path)
        self.mark_dirty(path)
    
    def _cache(self, path, obj, format):
        self._cached[path] = (obj, format)
    
    def remove(self, path):
        del self._cached[path]
        self._removed.add(path)

    def observer_for(self, path):
        return partial(self.mark_dirty, path)
    
    def mark_dirty(self, path):
        if path in self._removed:
            raise ValueError("cannot mark " + path + " as dirty: it has been removed")
        
        self._dirty.add(path)
    
    def flush(self):
        for path in self._dirty:
            self._flush_update(path)
        self._dirty.clear()
        
        for path in self._removed:
            self._flush_remove(path)
        self._removed.clear()
    
    def flush_file(self, path):
        if path in self._removed:
            self._flush_remove(path)
            self._removed.discard(path)
        elif path in self._dirty:
            self._flush_update(path)
            self._dirty.remove(path)

    def _flush_remove(self, path):
        self.storage.remove(path)
        
    def _flush_update(self, path):
        dirty_object, format = self._cached[path]
        with self.storage.open(path, "w") as output:
            format.save(dirty_object, output)
        


class YamlFormat(object):
    @staticmethod
    def load(input):
        return yaml.safe_load(input)
    
    @staticmethod
    def save(obj, output):
        yaml.safe_dump(obj, output, default_flow_style=False)


class TextFormat(object):
    @staticmethod
    def load(input):
        return input.read()
    
    @staticmethod
    def save(text, output):
        return output.write(text)
