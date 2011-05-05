
import os
import mmap

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper



class Deft:
    def __init__(self, abspath):
        pass


class Feature:
    def __init__(self, id, name, description, created_by):
        self.id = id
        self.name = name
        self.description = description
        self.status = "pending"
        self.created_by = created_by


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
    
    def __len__(self):
        return (len(self.mem) - self.offset) / self.line_length
        
    def __getitem__(self, n):
        if type(n) == int:
            return self._get_element(n)
        elif type(n) == slice:
            return self._get_slice(n)
        else:
            raise TypeError, "don't know how to index with a " + type(n) + ", should be an int or a slice"
        
    def _get_element(self, n):
        line_index = self._abs_index(n)
        
        return int(self._line(line_index).strip())
    
    def _abs_index(self, n):
        abs_index = n if n >= 0 else (len(self) + n)
        
        if not (0 <= abs_index < len(self)):
            raise IndexError, "cannot get element %d of %d"%(n, len(self))
        
        return abs_index
    
    def _get_slice(self, s):
        return [self._get_element(i) for i in range(*s.indices(len(self)))]
    

    def move(self, src, dst):
        if src == dst:
            return
        
        src = self._abs_index(src)
        dst = self._abs_index(dst)
        
        src_start = self._start_of(src)
        dst_start = self._start_of(dst)
        src_line = self._line(src)
        
        if src > dst:
            moved_mem_start = dst_start
            moved_mem_end = src_start
            moved_mem_dst = dst_start + self.line_length
        else:
            moved_mem_start = src_start + self.line_length
            moved_mem_end = dst_start + self.line_length
            moved_mem_dst = src_start
        
        moved_mem_size = moved_mem_end - moved_mem_start
        
        self.mem.move(moved_mem_dst, moved_mem_start, moved_mem_size)
        self.mem[dst_start:dst_start+self.line_length] = src_line
        self.mem.flush()
        
    def close(self):
        self.mem.close()
        self.file.close()
    
    def _start_of(self, n):
        return self.offset + self.line_length*n
    
    def _line(self, n):
        line_start = self._start_of(n)
        line_end = line_start + self.line_length
        return self.mem[line_start:line_end]
    
    def __enter__(self):
        return self

    def __exit__(self, *ignored):
        self.close()
