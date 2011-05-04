
import inspect
import os
from deft import Ordering

def ensure_dir_exists(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


class Ordering_Test:
    def test_ordering_is_created_empty(self):
        o = new_ordering()
        
        assert o.is_empty()


    def test_can_add_elements(self):
        o = new_ordering()
        
        o.add(10)
        o.add(20)
        o.add(30)
        o.add(40)
        
        assert not o.is_empty()
        assert o[0] == 10
        assert o[1] == 20
        assert o[2] == 30
        assert o[3] == 40
    
    
    def test_changes_are_persisted_to_mapped_file(self):
        o = new_ordering()
        o.add(10)
        o.add(20)
        o.add(30)
        o.add(40)
        
        o2 = new_ordering()
        assert not o2.is_empty()
        assert o2[0] == 10
        assert o2[1] == 20
        assert o2[2] == 30
        assert o2[3] == 40
    
    
def new_ordering():
    test_name = inspect.stack()[1][3]
    path = "output/testing/ordering_for_" + test_name
    ensure_dir_exists(os.path.dirname(path))
    return Ordering(path)

