from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple

from datastructures.avltree import AVLTree

#changes in the avl tree
#1. When placing duplicate keys in the tree, it will compare the values of the nodes and place it to the left or right based off that. 
# we need to define a method for comparison for this to work

#2. Added method for keys greater than and less than a certain value that will return a list of nodes that satisfy the condition
# This works relatively fast and is super useful in later functions 

#3. Implemented a delete that also takes into account a value to allow duplicates to be deleted


@dataclass
class Stock:
    symbol: str
    name: str
    high_price: float
    low_price: float
    max_price: float
    time: str

    #These allow a tie breaker if the low and high values are the same
    def __lt__(self, other: Stock):
        if self.symbol == other.symbol:
            if self.name == other.name:
                return self.time < other.time
            return self.name < other.name
        return self.symbol < other.symbol
    
    def __gt__(self, other: Stock):
        if self.symbol == other.symbol:
            if self.name == other.name:
                return self.time > other.time
            return self.name > other.name
        return self.symbol > other.symbol   


class IntervalNode:
    def __init__(self, key: int, value: Any, left: 'IntervalNode' = None, right: 'IntervalNode' = None, height: int = 1, max_end: int = 0, intervals_at_low: 'AVLTree' = None):
        #low values
        self.key = key

        #date we want to store besides the high and low values
        self.value = value

        #left and right children
        self.left = left
        self.right = right

        #height of the node(just like in the AVL tree)
        self.height = height

        #max high value for the node or its children
        self.max_end = max_end

        #tree containing all the data of values with the same low value
        self.intervals_at_low = intervals_at_low if intervals_at_low is not None else AVLTree()



class IntervalTree:
    def __init__(self):
        self._tree = AVLTree()
        self._total_entries = 0

    def insert(self, low: int, high: int, value: Any):
        #finds the node that has the same low value 
        node = self._tree.search(low)

        #if the node is found, then it enters another avl tree stored within the node and inserts the high value
        if node:
            node.value.intervals_at_low.insert(high, value)

        #if the node is not found, then it creates a new node with low value as key, enters the tree within the node
        else:
            new_node = IntervalNode(key=low, value=value, max_end=high)
            new_node.intervals_at_low.insert(high, value)
            self._tree.insert(low, new_node)

        self._update_max_end(self._tree.root)
        self._total_entries += 1
    
    def delete(self, low: int, high: Optional[int] = None):
        """
        Deletes an interval (low, high) from the interval tree. 
        If high is None, the node with the low key will be removed from the main tree.
        """
        node = self._tree.search(low)
        
        if not node:
            # If there's no node with this low value, return because nothing to delete
            return

        # If high is provided, remove from intervals_at_low (AVLTree for high values)
        node.value.intervals_at_low.delete(high)
        
        # If the intervals_at_low tree is now empty, remove the node from the main tree
        if node.value.intervals_at_low.is_empty():
            self._tree.delete(low)
        
        self._update_max_end(self._tree.root)
        self._total_entries -= 1
        return

    #Updates the max end value of the node by looking through its children and updating the max end value
    def _update_max_end(self, node: Optional[IntervalNode]):
        if not node:
            return 0
        
        left_max = self._update_max_end(node.left)
        right_max = self._update_max_end(node.right)
        self_max = node.value.intervals_at_low.max_key()
        node.max_end = max(left_max, right_max, self_max)
        return node.max_end 
    

    def n_lowest_lows(self, n: int):
        def _n_lowest_lows(node: Optional[IntervalNode], n: int, result: list):
            
            # If the node is none it doesn't change result at all 
            if not node or len(result) >= n:
                return result
            
            #Resursing down the left first 
            result = _n_lowest_lows(node.left, n, result)
            
            # If we have found the right amount, we return result
            if len(result) >= n:
                return result
            
            #If not we add the values of the current node to the result, we do inorder so it is secondarly sorted by high value
            node_list = node.value.intervals_at_low.inorder()
            for value in node_list:
                if len(result) < n:
                    result.append(value)
                #stops appending values if we have found the proper amount 
                else:
                    return result
            
            #This should catch the case where the last value fully fills result 
            if len(result) >= n:
                return result
            
            # Recurse to the right now
            return _n_lowest_lows(node.right, n, result)
        
        #kicks off recursion
        return _n_lowest_lows(self._tree.root, n, [])

    def n_highest_lows(self, n: int):
        def _n_highest_lows(node: Optional[IntervalNode], n: int, result: list):
            
            # If the node is none it doesn't change result at all 
            if not node or len(result) >= n:
                return result
            
            # Recurse down the right subtree first to get the higher lows
            result = _n_highest_lows(node.right, n, result)
            
            # If we have found enough elements, return the result
            if len(result) >= n:
                return result
            
            #Reversed the inorder traversal to get the highest values first
            node_list = node.value.intervals_at_low.inorder()[::-1]
            for value in node_list:  
                if len(result) < n:
                    result.append(value)
                else:
                    return result
            
            # If the result is full, return it
            if len(result) >= n:
                return result
            
            # Recurse to the left subtree now
            return _n_highest_lows(node.left, n, result)
        
        # Kick off recursion
        return _n_highest_lows(self._tree.root, n, [])



    def find_all_nodes_between_interval(self,low: int, high: int):
        nodes_between_list=[]

        #find nodes that satitsfy the condition of having a low value greater than the parameter low
        low_satisifying_nodes=self._tree.nodes_greater_than(low)

        for low_node in low_satisifying_nodes:
            nodes_between_list.extend(low_node.value.intervals_at_low.nodes_less_than(high))

        return nodes_between_list
    
    def find_nodes_that_overlap_with_interval(self,low: int, high: int):
        nodes_overlapping_list=[]

        #ones that satisfy the condition of having a low value less than the parameter high
        low_satisifying_nodes=self._tree.nodes_less_than(high)

        for node in low_satisifying_nodes:
            if node.max_end < low:
                continue
            else:
                for node2 in node.value.intervals_at_low.inorder():
                    if node2.key >= low:
                        nodes_overlapping_list.append(node2)
        return nodes_overlapping_list
    


    def find_nodes_containing_point(self, point: int):
        """
        Finds all intervals in the interval tree where the range (low, high) contains the given point.

        :param point: The specific point to check.
        :return: A list of interval values (e.g., 'A', 'B') that contain the point.
        """
        nodes_containing_point = []
        low_satisfying_nodes = self._tree.nodes_less_than(point)
        for node in low_satisfying_nodes:
            if node.max_end < point:
                continue
            else:
                for node2 in node.value.intervals_at_low.nodes_greater_than(point):
                    nodes_containing_point.append(node2)
        return nodes_containing_point
            


    
    def global_maximum(self):
        if not self._tree._root:
            return None
        return self._tree._root.max_end
    

    #returns the low values of the nodes that are the n lowest
    def percentile_id_calc(self, n: int):
        def _percentile_id_calc(node: Optional[IntervalNode], n: int, result: list, count=0):
            
            if not node or count >= n:
                return result, count
            
            # Recurse down the left subtree first
            result, count = _percentile_id_calc(node.left, n, result, count)
            
            if count >= n:
                return result, count
            
            # Add current node's values to the result
            count_increase = node.value.intervals_at_low.size()
            result.append(node.key)
            count += count_increase
            
            if count >= n:
                return result, count
            
            # Recurse to the right subtree
            return _percentile_id_calc(node.right, n, result, count)
        
        # Start the recursion and return just the result
        result, _ = _percentile_id_calc(self._tree.root, n, [])
        return result
    
    #This is finds the nearest whole percentile, should work better than with more values as it won't be rounding down as much 
    def percentile_calc(self, percent: float):
        id_amount = int(self._total_entries * percent)
        return self.percentile_id_calc(id_amount)[-1]