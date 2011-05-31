
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
    
    def exists(self, dirlist):
        return os.path.exists(self._to_path(dirlist))
    
    def open_read(self, dirlist):
        return open(self._to_path(dirlist), "r")
    
    def open_write(self, dirlist):
        self.makedirs(dirlist[:-1])
        return open(self._to_path(dirlist), "w")
    
    def remove(self, dirlist):
        path = self._to_path(dirlist)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.exists(path):
            os.remove(path)
    
    def list(self, patternlist):
        path_pattern = self._to_path(patternlist)
        for match in iglob(path_pattern):
            relmatch = os.path.relpath(match, start=self.basedir)
            yield relmatch.split(os.path.sep)
    
    def makedirs(self, dirlist):
        if dirlist:
            dirpath = self._to_path(dirlist)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

    def _to_path(self, dirlist):
        return os.path.join(self.basedir, *dirlist)

