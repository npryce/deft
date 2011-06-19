
from os.path import join
import yaml
from deft.tracker import FormatVersion as CurrentVersion
from deft.tracker import UserError, load_config_with_storage, ConfigFile


def upgrade(storage):
    config = load_config_with_storage(storage)
    storage_version = config["format"]
    
    if storage_version == CurrentVersion:
        raise UserError("already at version " + CurrentVersion)
    elif storage_version == "1.0":
        upgrade_from_1_0(storage, config)
    elif storage_version == "2.0":
        upgrade_from_2_0(storage, config)
    else:
        raise UserError("cannot upgrade from " + storage_version + " to " + CurrentVersion)
    
    assert config["format"] == CurrentVersion
    storage.save_yaml(ConfigFile, config)
    print "upgraded from version " + storage_version + " to " + CurrentVersion



def upgrade_from_2_0(storage, config):
    upgrade_2_0_to_2_1(storage, config)
    
def upgrade_from_1_0(storage, config):
    upgrade_1_0_to_2_0(storage, config)
    upgrade_from_2_0(storage, config)

def upgrade_2_0_to_2_1(storage, config):
    for status_file in storage.list(join(config["datadir"], "*.status")):
        properties_file = status_file[:-len("status")] + "properties.yaml"
        with open(properties_file, "w") as output:
            yaml.safe_dump({}, output, default_flow_style=False)
    
    config["format"] = "2.1"

def upgrade_1_0_to_2_0(storage, config):
    datadir = config["datadir"]
    status_files = storage.list(join(datadir, "*.status"))
    for f in status_files:
        yaml = storage.load_yaml(f)
        priority = yaml["priority"]
        status = yaml["status"]
        
        with open(f, "r") as output:
            output.write("{1:>8} {0}".format(status, priority))
    
    config["format"] = "2.0"

