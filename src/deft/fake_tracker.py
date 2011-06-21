
from collections import namedtuple
from deft.tracker import Feature


def make_features(n):
    return [make_feature(i) for i in xrange(0,n)]

def make_feature(i):
    return fake_feature(name=chr(ord('a')+i), priority=i+1)

class FakeFeature(object):
    def __init__(self, name="a-fake-feature", status="testing", priority=999, description="", properties=None):
        self.name = name
        self.status = status
        self.priority = priority
        self.description = description
        self.properties = properties or {}
        
    def _record_status(self, new_status):
        self.status = status
    
    def _record_priority(self, new_priority):
        self.priority = new_priority

def fake_feature(**kwargs):
    return FakeFeature(**kwargs)
