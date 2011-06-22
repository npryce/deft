
import sys
import itertools
import os
from glob import iglob
from deft.indexing import Bucket
from deft.storage import FileStorage, Cache, TextFormat, YamlFormat

FormatVersion = '2.1'

ConfigDir = ".deft"
ConfigFile = os.path.join(ConfigDir, "config")
DefaultDataDir = os.path.join(ConfigDir, "data")

StatusSuffix = ".status"
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
        self._cache = Cache(storage)
        self._index = {}
        
        self._index_features()
    
    def configure(self, **config):
        self.config.update(config)
        self.save_config()
    
    @property
    def initial_status(self):
        return self.config['initial_status']
    
    def save_config(self):
        self.storage.save_yaml(ConfigFile, self.config)
    
    def save(self):
        self._cache.flush()
    
    def create(self, name, status=None, description="", properties=None):
        if self._feature_exists_named(name):
            raise UserError("a feature already exists with name: " + name)
        
        if status is None:
            status = self.initial_status
        
        feature = Feature(tracker=self, name=name, status=status)
        feature_status_path = self._name_to_path(name,StatusSuffix)
        
        bucket = self.features_with_status(status)
        bucket.append(feature)
        
        self._cache.save(feature_status_path, feature, FeatureStatusFormat(self, name))
        self._cache.flush_file(feature_status_path)
        
        feature.description = description
        feature.properties = properties or {}
        
        return feature
    
    @property
    def statuses(self):
        return sorted([k for k in self._index.keys() if self._index[k]])
    
    def feature_named(self, name):
        if self._feature_exists_named(name):
            return self._load_feature(self._name_to_path(name))
        else:
            raise UserError("no feature named " + name)
    
    def features_with_status(self, status):
        return self._index.setdefault(status, Bucket([]))
    
    def all_features(self):
        return itertools.chain.from_iterable(self._index[status] for status in sorted(self._index))
    
    def purge(self, name):
        feature = self.feature_named(name)
        bucket = self.features_with_status(feature.status)
        
        bucket.remove(feature)
        
        self._cache.remove(self._name_to_path(name, StatusSuffix))
        self.storage.remove(self._name_to_path(name, DescriptionSuffix))
        self.storage.remove(self._name_to_path(name, PropertiesSuffix))
    
    def _change_name(self, feature, new_name):
        old_name = feature.name

        if new_name == old_name:
            return
        
        self._cache.remove(self._name_to_path(old_name, StatusSuffix))
        self._cache.save(self._name_to_path(new_name, StatusSuffix), feature, FeatureStatusFormat(self, new_name))
        feature._record_name(new_name)
        
        for suffix in [DescriptionSuffix, PropertiesSuffix]:
            self.storage.rename(self._name_to_path(old_name, suffix),
                                self._name_to_path(new_name, suffix))
        
    def _change_status(self, feature, new_status):
        old_bucket = self.features_with_status(feature.status)
        new_bucket = self.features_with_status(new_status)
        
        old_bucket.remove(feature)
        new_bucket.append(feature)
        feature._record_status(new_status)
        
    def _change_priority(self, feature, new_priority):
        bucket = self.features_with_status(feature.status)
        bucket.change_priority(feature, new_priority)
    
    def _feature_exists_named(self, name):
        return self._cache.exists(self._name_to_path(name))
    
    def _index_features(self):
        features_by_status = {}
        
        for f in self._load_features():
            features_by_status.setdefault(f.status, []).append(f)
        
        for status in features_by_status:
            self._index[status] = Bucket(features_by_status[status])
    
    def _load_features(self):
        return [self._load_feature(f) for f in self.storage.list(self._name_to_path("*"))]
    
    def _load_feature(self, path):
        return self._cache.load(path, FeatureStatusFormat(self, self._path_to_name(path)))
    
    def _load(self, path, format):
        with self.storage.open(path) as input:
            return format.load(input)
    
    def _save(self, path, data, format):
        with self.storage.open(path, "w") as output:
            return format.save(data, output)
    
    def _mark_dirty(self, feature):
        self._cache.mark_dirty(self._name_to_path(feature.name))
    
    def _name_to_path(self, name, suffix=StatusSuffix):
        return os.path.join(self.config["datadir"], name + suffix)
    
    def _path_to_name(self, path, suffix=StatusSuffix):
        return os.path.basename(path)[:-len(suffix)]
    
    def _name_to_real_path(self, name, suffix=StatusSuffix):
        return self.storage.abspath(self._name_to_path(name, suffix))


def _no_validation(value):
    pass

class FeatureFileProperty(object):
    def __init__(self, suffix, format, validate=_no_validation):
        self._suffix = suffix
        self._format = format
        self._validate = validate
    
    def __get__(self, feature, owner):
        return feature._load(self._suffix, self._format)
    
    def __set__(self, feature, value):
        self._validate(value)
        feature._save(self._suffix, value, self._format)


ReservedPropertyNames = frozenset(["status", "priority", "description"])

def validate_properties(properties):
    invalid_keys = set(properties.keys()).intersection(ReservedPropertyNames)
    if invalid_keys:
        raise UserError("feature properties cannot have the following reserved names: " + ", ".join(invalid_keys))


class Feature(object):
    def __init__(self, tracker, name, status, priority=None):
        self._name = name
        self._status = status
        self._priority = priority
        self._tracker = tracker
    
    def _get_name(self):
        return self._name
    
    def _set_name(self, new_name):
        self._tracker._change_name(self, new_name)
    
    def _record_name(self, new_name):
        self._name = new_name
        self._tracker._mark_dirty(self)
    
    name = property(_get_name, _set_name)
    
        
    def _get_status(self):
        return self._status
    
    def _set_status(self, new_status):
        self._tracker._change_status(self, new_status)
    
    def _record_status(self, new_status):
        self._status = new_status
        self._tracker._mark_dirty(self)
    
    status = property(_get_status, _set_status)
    
    def _get_priority(self):
        return self._priority
    
    def _set_priority(self, new_priority):
        self._tracker._change_priority(self, new_priority)
    
    def _record_priority(self, new_priority):
        self._priority = new_priority
        self._tracker._mark_dirty(self)
    
    priority = property(_get_priority, _set_priority)
    
    description = FeatureFileProperty(DescriptionSuffix, TextFormat)
    properties = FeatureFileProperty(PropertiesSuffix, YamlFormat, validate_properties)
    
    @property
    def description_file(self):
        return self._real_feature_file(DescriptionSuffix)
    
    @property
    def properties_file(self):
        return self._real_feature_file(PropertiesSuffix)
    
    def _load(self, suffix, format):
        return self._tracker._load(self._feature_file(suffix), format)

    def _save(self, suffix, data, format):
        return self._tracker._save(self._feature_file(suffix), data, format)
        
    def _feature_file(self, suffix):
        return self._tracker._name_to_path(self._name, suffix)

    def _real_feature_file(self, suffix):
        return self._tracker._name_to_real_path(self._name, suffix)
    
    def __str__(self):
        return self.__str__()
    
    def __repr__(self):
        return self.__class__.__name__ + \
            "(name=" + self._name + \
            ", status=" + self._status + \
            ", priority=" + str(self._priority) + ")"


    

class FeatureStatusFormat:
    def __init__(self, tracker, name):
        self.tracker = tracker
        self.name = name
    
    def load(self, input):
        text = input.read()
        priority = int(text[0:8])
        status = text[9:]
        return Feature(tracker=self.tracker, name=self.name, status=status, priority=priority)
    
    def save(self, feature, output):
        output.write("{1:>8} {0}".format(feature.status, feature.priority))
