
from os.path import join
from deft.tracker import FormatVersion as CurrentVersion
from deft.tracker import UserError, load_config_with_storage, ConfigFile
from deft.tracker import _format_status as format_status

def upgrade(storage):
    config = load_config_with_storage(storage)
    storage_version = config["format"]
    
    if storage_version == CurrentVersion:
        raise UserError("already at version " + CurrentVersion)
    elif storage_version == "1.0":
        upgrade_from_1_0(storage, config)
    else:
        raise UserError("cannot upgrade from " + storage_version + " to " + CurrentVersion)
    
    config["format"] = CurrentVersion
    storage.save_yaml(ConfigFile, config)
    print "upgraded from version " + storage_version + " to " + CurrentVersion


def upgrade_from_1_0(storage, config):
    datadir = config["datadir"]
    status_files = storage.list(join(datadir, "*.status"))
    for f in status_files:
        yaml = storage.load_yaml(f)
        priority = yaml["priority"]
        status = yaml["status"]
        
        storage.save_text(f, format_status(status, priority))
        
