
import os
import mmap


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
        new_feature.priority = len(self.features)
    
    def insert(self, new_feature):
        index = new_feature.priority - 1
        self.features.insert(index, new_feature)
        for f in self.features[index+1:]:
            f.priority = f.priority + 1
    
    def remove(self, feature):
        i = feature.priority-1
        del self.features[i]
        for f in self.features[i:]:
            f.priority = f.priority - 1
    
    def change_priority(self, feature, new_priority):
        """
        not efficient, but categorisation and prioritisation is all done by brute force 
        at the moment anyway, and disk access needs to be optimised, so this indexing
        class will be removed at some point.
        """
        
        self.remove(feature)
        feature.priority = new_priority
        self.insert(feature)
    
    def __str__(self):
        return self.__class__.__name__ + "(" + str([f for f in self.features]) + ")"
    
    def __repr__(self):
        return self.__class__.__name__ + "(" + repr([f for f in self.features]) + ")"
