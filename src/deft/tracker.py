
import os
from glob import iglob
import yaml

ConfigDir = ".deft"
ConfigFile = os.path.join(ConfigDir, "config")
DefaultDataDir = os.path.join(ConfigDir, "data")



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



class FeatureTracker:
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
        
        feature = Feature(name, status, description)
        feature.priority = priority
        
        save_yaml(self._name_to_path(feature.name), feature)
        
        return feature
    
    def list_status(self, status):
        l = [f for f in self._load_features_with_status(status)]
        return sorted(l, key = lambda f: f.priority)
    
    def close(self, name):
        os.remove(self._name_to_path(name))
    
    def _load_features_with_status(self, status):
        return [f for f in self._load_features() if f.status == status]
    
    def _load_features(self):
        return [load_yaml(f) for f in iglob(self._name_to_path("*"))]
    
    def _name_to_path(self, name):
        return os.path.join(os.path.join(self.config["datadir"], name + ".feature"))


class Feature(yaml.YAMLObject):
    yaml_tag="!deft/1.0/feature"
    yaml_loader = yaml.SafeLoader
    
    def __init__(self, name, status, description):
        self.name = name
        self.description = description
        self.status = status
        self.priority = None # Will be set by the FeatureTracker


