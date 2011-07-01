

import yaml


class StorageFormats(object):
    def save_yaml(self, relpath, obj):
        with self.open(relpath, "w") as output:
            yaml.safe_dump(obj, output, default_flow_style=False)
    
    def load_yaml(self, relpath):
        with self.open(relpath) as input:
            return yaml.safe_load(input)
    
    def save_text(self, relpath, text):
        with self.open(relpath, "w") as output:
            output.write(text)
            
    def load_text(self, relpath):
        with self.open(relpath) as input:
            return input.read()



class YamlFormat(object):
    @staticmethod
    def load(input):
        return yaml.safe_load(input)
    
    @staticmethod
    def save(obj, output):
        yaml.safe_dump(obj, output, default_flow_style=False)


class TextFormat(object):
    @staticmethod
    def load(input):
        return input.read()
    
    @staticmethod
    def save(text, output):
        return output.write(text)
