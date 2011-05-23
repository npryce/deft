
import os
from glob import iglob
import yaml

ConfigDir = ".deft"
ConfigFile = os.path.join(ConfigDir, "config")
DefaultDataDir = os.path.join(ConfigDir, "data")

FeatureSuffix = ".feature"


def save_yaml(path, obj):
    with open(path, "w") as output:
        yaml.dump(obj, output, default_flow_style=False)


def load_yaml(path):
    with open(path, "r") as input:
        return yaml.safe_load(input)


def save_text(path, text):
    with open(path, "w") as output:
        output.write(text)


def load_text(path):
    with open(path, "r") as input:
        return input.read()



class FeatureTracker(object):
    def __init__(self):
        if os.path.exists(ConfigFile):
            self.config = load_yaml(ConfigFile)
        else:
            self.config = {'datadir': DefaultDataDir, 'format': '0.1'}
    
            
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
        priority = len(self._load_features_with_status(status))
        feature = Feature(tracker=self, name=name, status=status, description=description, priority=priority)
        
        self._save_feature(feature)
        return feature
    
    def feature_named(self, name):
        return self._load_feature(self._name_to_path(name))
    
    def list_status(self, status):
        l = [f for f in self._load_features_with_status(status)]
        return sorted(l, key = lambda f: f.priority)
    
    def purge(self, name):
        os.remove(self._name_to_path(name))
    
    def _save_feature(self, feature):
        save_yaml(self._name_to_path(feature.name), {
                'status': feature.status,
                'priority': feature.priority,
                'description': feature.description
                })
    
    def _load_feature(self, path):
        return Feature(tracker=self, name=self._path_to_name(path), **load_yaml(path))
    
    def _load_features_with_status(self, status):
        return [f for f in self._load_features() if f.status == status]
    
    def _load_features(self):
        return [self._load_feature(f) for f in iglob(self._name_to_path("*"))]
    
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
            print "saving after setting attribute " + name + " to " + str(new_value)
            self._tracker._save_feature(self)
