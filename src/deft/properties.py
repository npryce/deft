

class Properties(dict):
    def append(self, name, value):
        if not name in self:
            self[name] = value
        elif type(self[name]) == list:
            self[name].append(value)
        else:
            self[name] = [self[name], value]
    
    
    def remove(self, name, value):
        if name in self:
            if type(self[name]) == list:
                self[name].remove(value)
                if len(self[name]) == 1:
                    self[name] = self[name][0]
            else:
                del self[name]
