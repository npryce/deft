
import os
from glob import iglob
from .fileops import *
from deft.indexing import Bucket

ConfigDir = ".deft"
ConfigFile = os.path.join(ConfigDir, "config")
DefaultDataDir = os.path.join(ConfigDir, "data")

FeatureSuffix = ".feature"




class FeatureTracker(object):
    def __init__(self):
        self._clear_cache()
        if os.path.exists(ConfigFile):
            self.config = load_yaml(ConfigFile)
        else:
            self.config = {'datadir': DefaultDataDir, 'format': '0.1'}
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        for feature in self._dirty:
            self._save_feature(feature)
        self._clear_cache()
    
    def _clear_cache(self):
        self._dirty = set()
        self._loaded = {}
    
    def init(self, **initial_config):
        if os.path.exists(ConfigDir):
            raise ValueError("tracker already initialised in directory " + ConfigDir)
        
        self.config.update(initial_config)
        
        os.mkdir(ConfigDir)
        os.makedirs(self.config['datadir'])
        self.save_config()
        
        
    def save_config(self):
        save_yaml(ConfigFile, self.config)
    
    
    def create(self, name, description, status):
        priority = len(self._load_features_with_status(status)) + 1
        feature = Feature(tracker=self, name=name, status=status, description=description, priority=priority)
        
        self._save_feature(feature)
        return feature
    
    def feature_named(self, name):
        return self._load_feature(self._name_to_path(name))
    
    def features_with_status(self, status):
        return Bucket(self._load_features_with_status(status))
    
    def purge(self, name):
        # Todo - remove from old status and update priorities of lower items
        os.remove(self._name_to_path(name))
    
    def change_status(self, feature, new_status):
        # Todo - remove from old status and update priorities of lower items
        feature.status = new_status
        # Todo - set priority as bottom of bucket
    
    def change_priority(self, feature, new_priority):
        bucket = self.features_with_status(feature.status)
        bucket.change_priority(feature, new_priority)
        
    def _load_features_with_status(self, status):
        return [f for f in self._load_features() if f.status == status]
    
    def _load_features(self):
        return [self._load_feature(f) for f in iglob(self._name_to_path("*"))]
    
    def _load_feature(self, path):
        if path in self._loaded:
            return self._loaded[path]
        else:
            feature = Feature(tracker=self, name=self._path_to_name(path), **load_yaml(path))
            self._loaded[path] = feature
            return feature
    
    def _mark_dirty(self, feature):
        self._dirty.add(feature)
    
    def _save_feature(self, feature):
        save_yaml(self._name_to_path(feature.name), {
                'status': feature.status,
                'priority': feature.priority,
                'description': feature.description
                })
    
    def _name_to_path(self, name):
        return os.path.join(os.path.join(self.config["datadir"], name + FeatureSuffix))
    
    def _path_to_name(self, path):
        return os.path.basename(path)[:-len(FeatureSuffix)]
    


class Feature(object):
    def __init__(self, tracker, name, status, priority, description):
        self.name = name
        self.status = status
        self.priority = priority
        self.description = description
        self._tracker = tracker
    
    def __setattr__(self, name, new_value):
        must_save = hasattr(self, '_tracker')
        object.__setattr__(self, name, new_value)
        if must_save:
            self._tracker._mark_dirty(self)
    
