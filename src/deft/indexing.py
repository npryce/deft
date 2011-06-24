
import os
import mmap
from itertools import count


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
    
    def rename(self, old_name, new_name):
        self._features_by_priority[self._index_of(old_name)] = new_name
        if self._priorities_by_feature is not None:
            self._priorities_by_feature[new_name] = self._priorities_by_feature[old_name]
            del self._priorities_by_feature[old_name]
        
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


