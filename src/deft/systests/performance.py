
import yaml
from StringIO import StringIO
import timeit

iters = 5000

class C:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name
        pass
    
obj = C(0, "name")


def write_yaml(obj, s):
    yaml.dump({'priority': obj.priority, 'name': obj.name}, s, default_flow_style=False)

def read_yaml(s):
    d = yaml.safe_load(s)
    return C(d['priority'], d['name'])


def round_trip(write, read):
    s = StringIO()
    write(obj, s)
    s.seek(0)
    read(s)
    
def print_timing(what, write, read):
    def doit():
        round_trip(write, read)
    
    total = timeit.timeit(doit, number=iters)
    print what, total

def read_feature(s):
    line = s.read()
    return C(int(line[0:8]), line[9:])

def write_feature(obj, s):
    s.write("{0:>8} {1}".format(obj.priority, obj.name))
    

print_timing("yaml", write_yaml, read_yaml)
print_timing("text", write_text, read_text)
