import pytest

from datastructures.intervaltree import IntervalTree
from datastructures.avltree import AVLTree
from datastructures.avltree import Node
from datastructures.intervaltree import IntervalNode

class TestIntervalTree:
    @pytest.fixture
    def intervaltree(self) -> IntervalTree:
        tree = IntervalTree()
    
    def test_insert(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A")
        tree.insert(5,15,"B")
        tree.insert(10,20,"C")
        tree.insert(7,15,"D")
        assert tree._tree.size()==3
        assert tree._tree.root.value.intervals_at_low.size()==2

    def test_find_nodes_between(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A") #
        tree.insert(5,15,"B") #
        tree.insert(10,20,"C")
        tree.insert(7,15,"D") #
        nodes_selected = tree.find_all_nodes_between_interval(5,15)
        value_list = []
        for node in nodes_selected:
            value_list.append(node.value)
        assert set(value_list) == set(["A","B","D"])

    def test_find_nodes_overlapping(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A") 
        tree.insert(5,15,"B") 
        tree.insert(10,20,"C")
        tree.insert(7,16,"D") 
        tree.insert(40,50,"E")
        nodes_selected = tree.find_nodes_that_overlap_with_interval(15,30)
        value_list = []
        for node in nodes_selected:
            value_list.append(node.value)
        assert set(value_list) == set(["B","C","D"])

    def test_max_end(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A") 
        tree.insert(5,15,"B") 
        tree.insert(10,20,"C")
        tree.insert(7,15,"D") 
        tree.insert(40,50,"E")
        assert tree._tree.root.max_end==50

    def test_find_nodes_containing_point(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A") #
        tree.insert(5,15,"B") #
        tree.insert(10,20,"C")
        tree.insert(7,15,"D") #
        tree.insert(40,50,"E")
        assert len(tree.find_nodes_containing_point(8))==3
    
    def test_find_n_lowest_lows(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A")
        tree.insert(5,15,"B")
        tree.insert(10,20,"C")
        tree.insert(7,15,"D")
        tree.insert(40,50,"E")
        values = []
        for node in tree.n_lowest_lows(3):
            values.append(node.value)
        assert values == ["B","A","D"]

    def test_find_n_highest_lows(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A")
        tree.insert(5,15,"B")
        tree.insert(10,20,"C")
        tree.insert(7,15,"D")
        tree.insert(40,50,"E")
        values = []
        for node in tree.n_highest_lows(3):
            values.append(node.value)
        assert values == ["E","C","D"]

    def test_percentile_calculator(self, intervaltree):
        tree = IntervalTree()
        tree.insert(0,10,"A")
        tree.insert(0,15,"B")
        tree.insert(20,20,"C")
        tree.insert(40,15,"D")
        tree.insert(40,50,"E")
        assert tree.percentile_calc(.6)==20
        assert tree.percentile_calc(.8)==40
        assert tree.percentile_calc(.2)==0

    def test_delete(self, intervaltree):
        tree = IntervalTree()
        tree.insert(7,10,"A")
        tree.insert(5,15,"B")
        tree.insert(10,20,"C")
        tree.delete(7,10)
        assert tree._tree.size()==2