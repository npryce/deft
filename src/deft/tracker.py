
import sys
from functools import partial
import itertools
import os
from glob import iglob
from deft.indexing import PriorityIndex
from deft.storage import FileStorage, TextFormat, YamlFormat

FormatVersion = '3.0'

ConfigDir = ".deft"
ConfigFile = os.path.join(ConfigDir, "config")
DefaultDataDir = os.path.join(ConfigDir, "data")

StatusIndexSuffix = ".index"
DescriptionSuffix = ".description"
PropertiesSuffix = ".properties.yaml"

# Used to report user errors that have been explicitly detected
class UserError(Exception):
    pass


def default_config(datadir=DefaultDataDir, initial_status="new"):
    return {
        'format': FormatVersion,
        'datadir': datadir,
        'initial_status': initial_status}

def init_tracker(**config_overrides):
    return init_with_storage(FileStorage(os.getcwd()), config_overrides)


def tracker_storage():
    basedir = os.path.abspath(os.getcwd())
    while not os.path.exists(os.path.join(basedir, ConfigDir)):
        parent = os.path.dirname(basedir)
        if parent == basedir:
            # At root directory (there is no API call to test this)
            raise UserError("no tracker found in " + os.getcwd() + " or directories above " + os.getcwd())
        else:
            basedir = parent

    return FileStorage(basedir)

def load_tracker():
    return load_with_storage(tracker_storage())

def init_with_storage(storage, config_overrides):
    if storage.exists(ConfigDir):
        raise UserError("tracker already initialised in directory " + ConfigDir)
    
    tracker = FeatureTracker(default_config(**config_overrides), storage)
    tracker.save_config()
    
    return tracker

def load_with_storage(storage):
    return FeatureTracker(load_config_with_storage(storage), storage)

def load_config_with_storage(storage):
    if not storage.exists(ConfigDir):
        raise UserError("tracker not initialised")
    
    return storage.load_yaml(ConfigFile)


class FeatureTracker(object):
    def __init__(self, config, storage):
        repo_format = config['format']
        if repo_format != FormatVersion:
            raise UserError("incompatible tracker: found data in format version %s, " \
                            "requires data in format version %s"%(repo_format, FormatVersion))
        
        self.config = config
        self.storage = storage
        self._name_index = {}
        self._status_index = {}
        
        self._index_features()
    
    def _index_features(self):
        for f in self.storage.list(self._status_path("*")):
            status = os.path.basename(f)[:-(len(StatusIndexSuffix))]
            with self.storage.open(f) as input:
                feature_names = input.read().splitlines()
            
            self._status_index[status] = PriorityIndex(feature_names)
            
            for name in feature_names:
                self._name_index[name] = Feature(tracker=self, name=name, status=status)
    
    def configure(self, **config):
        self.config.update(config)
        self.save_config()
    
    @property
    def initial_status(self):
        return self.config['initial_status']
    
    def save_config(self):
        self.storage.save_yaml(ConfigFile, self.config)
    
    def save(self):
        pass
    
    def create(self, name, status=None, description="", properties=None):
        if self._has_feature_named(name):
            raise UserError("a feature already exists with name: " + name)
        
        if status is None:
            status = self.initial_status
        
        feature = Feature(tracker=self, name=name, status=status)
        feature.description = description
        feature.properties = properties or {}
        
        self._name_index[name] = feature
        
        status_index = self._status(status)
        status_index.append(name)
        
        self._save_status_index(status)
        
        return feature
    
    @property
    def statuses(self):
        return sorted([k for k in sorted(self._status_index.keys()) if self._status_index[k]])
    
    def feature_named(self, name):
        if self._has_feature_named(name):
            return self._name_index[name]
        else:
            raise UserError("no feature named " + name)
    
    def features_with_status(self, status):
        return [self.feature_named(n) for n in self._status(status)]
    
    def all_features(self):
        return (self.feature_named(n) for n in itertools.chain.from_iterable(
                self._status(s) for s in sorted(self._status_index)))
    
    def purge(self, name):
        feature = self.feature_named(name)
        self._status(feature.status).remove(name)
        del self._name_index[name]
        
        self._save_status_index(feature.status)
        self.storage.remove(self._feature_path(name, DescriptionSuffix))
        self.storage.remove(self._feature_path(name, PropertiesSuffix))
    
    def _change_name(self, feature, new_name):
        old_name = feature.name
        
        if new_name == old_name:
            return
        
        if new_name in self._name_index:
            raise UserError("a feature named " + repr(new_name) + " already exists")
        
        self._status(feature.status).rename(old_name, new_name)
        del self._name_index[old_name]
        self._name_index[new_name] = feature
        
        self._save_status_index(feature.status)
        
        for suffix in [DescriptionSuffix, PropertiesSuffix]:
            self.storage.rename(self._feature_path(old_name, suffix),
                                self._feature_path(new_name, suffix))
        
    def _change_status(self, feature, new_status):
        old_status = feature.status
        
        old_index = self._status(old_status)
        new_index = self._status(new_status)
        
        old_index.remove(feature.name)
        new_index.append(feature.name)
        
        self._save_status_index(old_status)
        self._save_status_index(new_status)


    def _priority_of(self, feature):
        return self._status(feature.status).priority_of_feature(feature.name)
        
    def _change_priority(self, feature, new_priority):
        index = self._status(feature.status)
        index.change_priority(feature.name, new_priority)
        self._save_status_index(feature.status)
    
    def _status(self, status):
        return self._status_index.setdefault(status, PriorityIndex([]))
    
    def _save_status_index(self, status):
        with self.storage.open(self._status_path(status), "w") as output:
            for feature_name in self._status(status):
                output.writelines(feature_name+"\n")
    
    def _has_feature_named(self, name):
        return name in self._name_index
    
    def _load(self, path, format):
        with self.storage.open(path) as input:
            return format.load(input)
    
    def _save(self, path, data, format):
        with self.storage.open(path, "w") as output:
            return format.save(data, output)
        
    def _status_path(self, status):
        return os.path.join(self.config["datadir"], "status", status+ StatusIndexSuffix)
        
    def _feature_path(self, name, suffix):
        return os.path.join(self.config["datadir"], "features", name + suffix)
    
    def _feature_abspath(self, name, suffix):
        return self.storage.abspath(self._feature_path(name, suffix))


class FeatureFileProperty(object):
    def _no_validation(value):
        pass
    
    def __init__(self, suffix, format, validate=_no_validation):
        self._suffix = suffix
        self._format = format
        self._validate = validate
    
    def __get__(self, feature, owner):
        return feature._tracker._load(feature._path(self._suffix), self._format)
    
    def __set__(self, feature, new_value):
        self._validate(new_value)
        feature._tracker._save(feature._path(self._suffix), new_value, self._format)


ReservedPropertyNames = frozenset(["status", "priority", "description"])

def validate_properties(properties):
    invalid_keys = set(properties.keys()).intersection(ReservedPropertyNames)
    if invalid_keys:
        raise UserError("feature properties cannot have the following reserved names: " + ", ".join(invalid_keys))


class TrackedProperty(object):
    def __init__(self, field_name, change_request_fn):
        self._field_name = field_name
        self._change_request_fn = change_request_fn
    
    def __get__(self, feature, owner):
        return getattr(feature, self._field_name)

    def __set__(self, feature, new_value):
        self._change_request_fn(feature._tracker, feature, new_value)
        setattr(feature, self._field_name, new_value)


class Feature(object):
    def __init__(self, tracker, name, status, priority=None):
        self._name = name
        self._status = status
        self._priority = priority
        self._tracker = tracker
    
    name = TrackedProperty("_name", FeatureTracker._change_name)
    status = TrackedProperty("_status", FeatureTracker._change_status)
    priority = property(
        lambda self: self._tracker._priority_of(self),
        lambda self, new_priority: self._tracker._change_priority(self, new_priority))
    description = FeatureFileProperty(DescriptionSuffix, TextFormat)
    properties = FeatureFileProperty(PropertiesSuffix, YamlFormat, validate_properties)
    
    @property
    def description_file(self):
        return self._abspath(DescriptionSuffix)
    
    @property
    def properties_file(self):
        return self._abspath(PropertiesSuffix)
    
    def _path(self, suffix):
        return self._tracker._feature_path(self._name, suffix)
    
    def _abspath(self, suffix):
        return self._tracker._feature_abspath(self._name, suffix)
    
    def __str__(self):
        return self.__str__()
    
    def __repr__(self):
        return self.__class__.__name__ + \
            "(name=" + self.name + \
            ", status=" + self.status + \
            ", priority=" + str(self.priority) + ")"

