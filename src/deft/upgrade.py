
import itertools
import os
from os.path import join, basename
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
    elif storage_version == "2.1":
        upgrade_from_2_1(storage, config)
    else:
        raise UserError("cannot upgrade from " + storage_version + " to " + CurrentVersion)
    
    assert config["format"] == CurrentVersion
    storage.save_yaml(ConfigFile, config)
    print "upgraded from version " + storage_version + " to " + CurrentVersion


def upgrade_from_2_1(storage, config):
    upgrade_2_1_to_3_0(storage, config)

def upgrade_from_2_0(storage, config):
    upgrade_2_0_to_2_1(storage, config)
    upgrade_from_2_1(storage, config)
    
def upgrade_from_1_0(storage, config):
    upgrade_1_0_to_2_0(storage, config)
    upgrade_from_2_0(storage, config)


def upgrade_2_1_to_3_0(storage, config):
    for f in itertools.chain(storage.list(join(config["datadir"], "*.description")),
                             storage.list(join(config["datadir"], "*.properties.yaml"))):
        storage.rename(f, join(config["datadir"], "features", basename(f)))
    
    statuses = {}
    status_ext = ".status"
    for f in storage.list(join(config["datadir"], "*"+status_ext)):
        line = open(f).read()
        
        feature_name = basename(f)[:-len(status_ext)]
        priority = int(line[:8])
        status = line[9:]
        
        statuses.setdefault(status, []).append((priority, feature_name))
        
        storage.remove(f)
    
    for status in statuses:
        with storage.open(join(config["datadir"], "status", status + ".index"), "w") as output:
            for (priority, feature_name) in sorted(statuses[status]):
                output.write(feature_name)
                output.write(os.linesep)
    
    
    config["format"] = "3.0"

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

