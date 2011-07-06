
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


class LinesFormat(object):
    def __init__(self, sequence_type):
        self.sequence_type = sequence_type
    
    def load(self, input):
        return self.sequence_type(input.read().splitlines())
    
    def save(self, lines, output):
        for line in lines:
            output.write(line)
            output.write("\n")
