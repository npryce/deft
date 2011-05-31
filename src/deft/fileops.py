
import os
import shutil
import yaml


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


def ensure_dir_exists(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def ensure_dir_not_exists(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)

def ensure_empty_dir_exists(dirpath):
    ensure_dir_not_exists(dirpath)
    ensure_dir_exists(dirpath)



