
import os
from glob import iglob
import uuid
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
        self.config = load_yaml(ConfigFile)
    
    def create(self, name, description, status):
        priority = len(self._load_features_with_status(status))
        
        feature = Feature(self._next_id(), name, status, description)
        feature.priority = priority
        
        save_yaml(self._id_to_path(feature.id), feature)
        
        return feature
    
    def list_status(self, status):
        l = [f for f in self._load_features_with_status(status)]
        return sorted(l, key = lambda f: f.priority)
    
    def close(self, id):
        os.remove(self._id_to_path(id))
    
    def _next_id(self):
        return uuid.uuid4().hex
    
    def _load_features_with_status(self, status):
        return [f for f in self._load_features() if f.status == status]
    
    def _load_features(self):
        return [load_yaml(f) for f in iglob(self._id_to_path("*"))]
    
    def _id_to_path(self, id):
        return os.path.join(os.path.join(self.config["datadir"], id + ".feature"))


class Feature(yaml.YAMLObject):
    yaml_tag="!deft/1.0/feature"
    yaml_loader = yaml.SafeLoader
    
    def __init__(self, id, name, status, description):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.priority = None # Will be set by the FeatureTracker
    

def init_tracker(datadir):
    if os.path.exists(ConfigDir):
        raise ValueError("tracker already initialised in directory " + ConfigDir)
    
    os.mkdir(ConfigDir)
    os.makedirs(datadir)
    save_yaml(ConfigFile, {'datadir': datadir, 'format': '0.1'})

