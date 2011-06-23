
import os
import mmap
from itertools import count

class Bucket:
    def __init__(self, unsorted_features):
        self.features = sorted(unsorted_features, key=lambda f: f.priority)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, n):
        return self.features[n]
    
    def __iter__(self):
        return self.features.__iter__()
    
    def append(self, new_feature):
        self.features.append(new_feature)
        new_feature._record_priority(len(self.features))
    
    def insert(self, new_feature):
        index = new_feature.priority - 1
        self.features.insert(index, new_feature)
        for f in self.features[index+1:]:
            f._record_priority(f.priority + 1)
    
    def remove(self, feature):
        i = feature.priority-1
        del self.features[i]
        for f in self.features[i:]:
            f._record_priority(f.priority - 1)
    
    def change_priority(self, feature, new_priority):
        """
        not efficient, but categorisation and prioritisation is all done by brute force 
        at the moment anyway, and disk access needs to be optimised, so this indexing
        class will be removed at some point.
        """
        
        self.remove(feature)
        feature._record_priority(new_priority)
        self.insert(feature)
    
    def __str__(self):
        return self.__class__.__name__ + "(" + str([f for f in self.features]) + ")"
    
    def __repr__(self):
        return self.__class__.__name__ + "(" + repr([f for f in self.features]) + ")"


class PriorityIndex:
    def __init__(self, feature_names_in_priority_order):
        self._features_by_priority = list(feature_names_in_priority_order)
        self._priorities_by_feature = None
    
    def __len__(self):
        return len(self._features_by_priority)
    
    def __iter__(self):
        return iter(self._features_by_priority)
    
    def feature_with_priority(self, n):
        return self._features_by_priority[n-1]
    
    def priority_of_feature(self, feature_name):
        if self._priorities_by_feature is None:
            self._priorities_by_feature = dict(zip(self._features_by_priority, count(1)))
        
        return self._priorities_by_feature[feature_name]
    
    def append(self, new_feature_name):
        self._features_by_priority.append(new_feature_name)
        if self._priorities_by_feature is not None:
            self._priorities_by_feature[new_feature_name] = len(self._features_by_priority)
    
    def insert(self, new_feature_name, priority):
        self._features_by_priority.insert(max(0, priority-1), new_feature_name)
        self._priorities_changed()
    
    def remove(self, feature_name):
        del self._features_by_priority[self._index_of(feature_name)]
        self._priorities_changed()
    
    def change_priority(self, feature_name, new_priority):
        self.remove(feature_name)
        self.insert(feature_name, new_priority)
    
    def _priorities_changed(self):
        self._priorities_by_feature = None
    
    def _index_of(self, feature_name):
        if self._priorities_by_feature is not None:
            return self._priorities_by_feature[feature_name]-1
        else:
            return self._features_by_priority.index(feature_name)
        
    def __str__(self):
        return repr(self)
    
    def __repr__(self):
        return self.__class__.__name__ + "([" + ", ".join(map(repr, self._features_by_priority)) + "])"


