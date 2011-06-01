
import os
import shutil
from glob import iglob
import yaml


class StorageFormats(object):
    def save_yaml(self, dirlist, obj):
        with self.open_write(dirlist) as output:
            yaml.dump(obj, output, default_flow_style=False)
    
    def load_yaml(self, dirlist):
        with self.open_read(dirlist) as input:
            return yaml.safe_load(input)
    
    def save_text(self, dirlist, text):
        with self.open_write(dirlist) as output:
            output.write(text)
            
    def load_text(self, dirlist):
        with self.open_read(dirlist) as input:
            return input.read()


class FileStorage(StorageFormats):
    def __init__(self, basedir):
        self.basedir = basedir
    
    def exists(self, relpath):
        return os.path.exists(self._to_path(relpath))
    
    def open_read(self, relpath):
        return open(self._to_path(relpath), "r")
    
    def open_write(self, relpath):
        self.makedirs(os.path.dirname(relpath))
        return open(self._to_path(relpath), "w")
    
    def remove(self, relpath):
        path = self._to_path(relpath)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
    
    def list(self, relpattern):
        pattern = self._to_path(relpattern)
        return (os.path.relpath(match, start=self.basedir) for match in iglob(pattern))
    
    def makedirs(self, relpath):
        if relpath != "":
            dirpath = self._to_path(relpath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
    
    def _to_path(self, relpath):
        return os.path.join(self.basedir, relpath)

