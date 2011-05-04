
import os
import mmap

class Ordering:
    max_digits = 7
    line_length = max_digits+1
    header = 'V1.0 W%d\n'%max_digits
    offset = len(header)
    
    def __init__(self, path):
        new_file = not os.path.exists(path)
        self.file = open(path, "a+b")
        if new_file:
            self.file.seek(0)
            self.file.write(self.header)
            self.file.flush()
        
        self.mem = mmap.mmap(self.file.fileno(), 0)
    
    def is_empty(self):
        return len(self.mem) == self.offset
    
    def add(self, id):
        new_line = "% *d\n"%(self.max_digits,id)
        end = len(self.mem)
        self.mem.resize(end+len(new_line))
        self.mem.seek(end)
        self.mem.write(new_line)
        self.mem.flush()
    
    def __getitem__(self, n):
        line_start = self.offset + self.line_length*n
        line_end = line_start + self.line_length
        line = self.mem[line_start:line_end]
        return int(line.strip())
    
    def close(self):
        self.mem.close()
        self.file.close()
