

from deft.tracker import Feature

class FakeTracker:
    def _mark_dirty(self, feature):
        pass

fake_tracker = FakeTracker()

def make_features(n):
    return [make_feature(i) for i in xrange(0,n)]

def make_feature(i):
    return fake_feature(name=chr(ord('a')+i), priority=i+1)

def fake_feature(name="a-fake-feature", priority=999, status="testing"):
    return Feature(tracker=fake_tracker, name=name, priority=priority, status=status)
