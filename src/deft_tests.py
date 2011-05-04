
import inspect
import os
import shutil
from deft import Ordering


class Ordering_Test:
    @classmethod
    def outdir(c):
        return "output/testing/" + c.__name__
    
    @classmethod
    def setup_class(c):
        ensure_dir_not_exists(c.outdir())
    
    
    def test_ordering_is_created_empty(self):
        o = new_ordering()
        
        assert o.is_empty()


    def test_adds_and_gets_elements(self):
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
    
    def test_can_index_from_end(self):
        o = new_ordering()
        o.add(9)
        o.add(10)
        o.add(11)
        o.add(12)
        o.add(13)
        
        assert o[-1] == 13
        assert o[-2] == 12
        assert o[-3] == 11
        assert o[-4] == 10
        assert o[-5] == 9
    
    def test_can_be_sliced(self):
        o = new_ordering()
        for i in range(1,11):
            o.add(i*10)
        
        assert o[0:2] == [10,20]
        assert o[1:5] == [20,30,40,50]
        assert o[-3:-1] == [80,90]
        assert o[8:] == [90,100]
        assert o[:] == [10,20,30,40,50,60,70,80,90,100]
    
    def test_reports_if_positive_index_out_of_bounds(self):
        o = new_ordering()
        o.add(1)
        o.add(2)
        
        try:
            o[2]
        except IndexError:
            return
        
        assert False, "should have thrown IndexError"
    
    
    def test_reports_if_negative_index_out_of_bounds(self):
        o = new_ordering()
        o.add(1)
        o.add(2)
        
        try:
            o[-3]
        except IndexError:
            return
        
        raise AssertionError, "should have thrown IndexError"
            

    def test_changes_are_persisted_to_mapped_file(self):
        o = new_ordering()
        o.add(101)
        o.add(100)
        o.add(99)
        
        o2 = new_ordering()
        assert not o2.is_empty()
        assert o2[0] == 101
        assert o2[1] == 100
        assert o2[2] == 99
    
    
    def test_reports_length(self):
        o = new_ordering()
        assert len(o) == 0
        
        o.add(1)
        assert len(o) == 1
        
        o.add(2)
        assert len(o) == 2
        
        o.add(3)
        assert len(o) == 3
    
        
    def test_can_move_items_up_in_ordering(self):
        o = new_ordering()
        o.add(11)
        o.add(22)
        o.add(33)
        o.add(44)
        o.add(55)
        
        o.move(src=3, dst=1)
        
        new_order = new_ordering()[:]
        assert new_order == [11, 44, 22, 33, 55]

    
    def test_can_move_items_down_in_ordering(self):
        o = new_ordering()
        o.add(0)
        o.add(1)
        o.add(2)
        o.add(3)
        o.add(4)
        
        o.move(src=1, dst=3)
        
        new_order = new_ordering()[:]
        assert new_order == [0, 2, 3, 1, 4]


def new_ordering():
    test_name = inspect.stack()[1][3]
    
    ensure_dir_exists(Ordering_Test.outdir())
    return Ordering(Ordering_Test.outdir() + "/" + test_name)

def ensure_dir_exists(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)


def ensure_dir_not_exists(dirpath):
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
