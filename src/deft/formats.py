
import yaml

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
