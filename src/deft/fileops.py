
import os
import shutil
import yaml


def ensure_dir_exists(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def ensure_dir_not_exists(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)

def ensure_empty_dir_exists(dirpath):
    ensure_dir_not_exists(dirpath)
    ensure_dir_exists(dirpath)



