
import os
from glob import iglob
from .fileops import *
from deft.indexing import Bucket

ConfigDir = ".deft"
ConfigFile = os.path.join(ConfigDir, "config")
DefaultDataDir = os.path.join(ConfigDir, "data")

PropertiesSuffix = ".yaml"
DescriptionSuffix = ".description"

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
    
    tracker = FeatureTracker(config)
    tracker.save_config()
    
    return tracker


def load():
    if not os.path.exists(ConfigDir):
        raise UserError("tracker not initialised")
    return FeatureTracker(load_yaml(ConfigFile))


class FeatureTracker(object):
    def __init__(self, config):
        self.config = config
        self._init_empty_cache()
    
    def configure(self, **config):
        self.config.update(config)
        self.save_config()
    
    @property
    def initial_status(self):
        return self.config['initial_status']
    
    def save_config(self):
        save_yaml(ConfigFile, self.config)
    
    def save(self):
        for feature in self._dirty:
            self._save_feature(feature)
        self._init_empty_cache()
    
    def _init_empty_cache(self):
        self._dirty = set()
        self._loaded = {}
    
    def create(self, name, status, initial_description=""):
        if self._feature_exists_named(name):
            raise UserError("a feature already exists with name: " + name)
        
        priority = len(self._load_features_with_status(status)) + 1
        
        feature = Feature(tracker=self, name=name, status=status, priority=priority)
        
        self._save_feature(feature)
        feature.write_description(initial_description)
        
        return feature
    
    def feature_named(self, name):
        if self._feature_exists_named(name):
            return self._load_feature(self._name_to_path(name))
        else:
            raise UserError("no feature named " + name)
    
    def features_with_status(self, status):
        return Bucket(self._load_features_with_status(status))
    
    def all_features(self):
        return sorted(self._load_features(), key=lambda f: (f.status, f.priority))
    
    def purge(self, name):
        properties_path = self._name_to_path(name, PropertiesSuffix)
        description_path = self._name_to_path(name, DescriptionSuffix)
        
        feature = self._load_feature(properties_path)
        bucket = self.features_with_status(feature.status)
        
        bucket.remove(feature)
        
        del self._loaded[properties_path]
        self._dirty.discard(feature)
        
        os.remove(properties_path)
        os.remove(description_path)
    
    
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
        save_yaml(self._name_to_path(feature.name),
                  {'status': feature.status, 'priority': feature.priority})
    
    def _write_description(self, feature, description):
        save_text(self._name_to_path(feature.name, DescriptionSuffix), description)

    def _name_to_path(self, name, suffix=PropertiesSuffix):
        return os.path.join(os.path.join(self.config["datadir"], name + suffix))
    
    def _path_to_name(self, path, suffix=PropertiesSuffix):
        return os.path.basename(path)[:-len(suffix)]
    


class Feature(object):
    def __init__(self, tracker, name, status, priority):
        self.name = name
        self.status = status
        self.priority = priority
        self._tracker = tracker
    
    def __setattr__(self, name, new_value):
        must_save = hasattr(self, '_tracker')
        object.__setattr__(self, name, new_value)
        if must_save:
            self._tracker._mark_dirty(self)
    
    @property
    def description_file(self):
        return self._tracker._name_to_path(self.name, DescriptionSuffix)
    
    def write_description(self, description):
        self._tracker._write_description(self, description)
    
