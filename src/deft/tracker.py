
import os
from glob import iglob
from .fileops import *
from deft.indexing import Bucket

ConfigDir = ".deft"
ConfigFile = os.path.join(ConfigDir, "config")
DefaultDataDir = os.path.join(ConfigDir, "data")

FeatureSuffix = ".feature"

# Used to report user errors that have been explicitly detected
class UserError(Exception):
    pass


def init(**initial_config):
    if os.path.exists(ConfigDir):
        raise UserError("tracker already initialised in directory " + ConfigDir)
    
    config = {
        'format': '0.1',
        'datadir': DefaultDataDir,
        'initial_status': "new"}
    config.update(initial_config)
    
    os.mkdir(ConfigDir)
    os.makedirs(config['datadir'])
    save_config(config)
    
    return load()


def save_config(config):
    save_yaml(ConfigFile, config)


def load():
    return FeatureTracker()


class FeatureTracker(object):
    def __init__(self):
        if not os.path.exists(ConfigDir):
            raise UserError("tracker not initialised")
        self._clear_cache()
        self.config = load_yaml(ConfigFile)
    
    def configure(self, **config):
        self.config.update(config)
        save_config(self.config)
    
    @property
    def initial_status(self):
        return self.config['initial_status']
    
    def save(self):
        for feature in self._dirty:
            self._save_feature(feature)
        self._clear_cache()
    
    def _clear_cache(self):
        self._dirty = set()
        self._loaded = {}
    
    def create(self, name, description, status):
        if self._feature_exists_named(name):
            raise UserError("a feature already exists with name: " + name)
        
        priority = len(self._load_features_with_status(status)) + 1
        feature = Feature(tracker=self, name=name, status=status, description=description, priority=priority)
        
        self._save_feature(feature)
        return feature
    
    def feature_named(self, name):
        return self._load_feature(self._name_to_path(name))
    
    def features_with_status(self, status):
        return Bucket(self._load_features_with_status(status))
    
    def all_features(self):
        return sorted(self._load_features(), key=lambda f: (f.status, f.priority))
    
    def purge(self, name):
        feature_path = self._name_to_path(name)
        feature = self._load_feature(feature_path)
        
        bucket = self.features_with_status(feature.status)
        bucket.remove(feature)
        
        del self._loaded[feature_path]
        self._dirty.discard(feature)
        
        os.remove(feature_path)
    
    
    def change_status(self, feature, new_status):
        old_bucket = self.features_with_status(feature.status)
        new_bucket = self.features_with_status(new_status)
        
        old_bucket.remove(feature)
        new_bucket.append(feature)
        feature.status = new_status
    
    
    def change_priority(self, feature, new_priority):
        bucket = self.features_with_status(feature.status)
        bucket.change_priority(feature, new_priority)
    
    def _feature_exists_named(self, name):
        return os.path.exists(self._name_to_path(name))
    
    def _load_features_with_status(self, status):
        return [f for f in self.all_features() if f.status == status]
    
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
    
