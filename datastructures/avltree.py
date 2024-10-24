from __future__ import annotations
from datastructures.iavltree import IAVLTree
from typing import Any, Callable, Protocol, TypeVar, Generic, Optional, List
from collections import deque

class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...



K = TypeVar('K', bound=Comparable)  # Key type for ordering the nodes
V = TypeVar('V')  # Value type for storing associated data


class Node:
        def __init__(self, key: K, value: V, height=1):
            self.key = key
            self.value = value
            self.height = height
            self.left = None
            self.right = None

def height(node: Node):
    if not node:
        return 0
    return node.height

def get_balance(node: Node):
    return height(node.left if node.left else 0) - height(node.right if node.right else 0)

def right_rotate(node1: Node):
    node2 = node1.left
    T2 = node2.right

    node2.right = node1
    node1.left = T2

    node1.height = 1 + max(height(node1.left), height(node1.right))
    node2.height = 1 + max(height(node2.left), height(node2.right))

    return node2

def left_rotate(node1: Node):
    node2 = node1.right
    T2 = node2.left

    node2.left = node1
    node1.right = T2

    node1.height = 1 + max(height(node1.left), height(node1.right))
    node2.height = 1 + max(height(node2.left), height(node2.right))

    return node2

def balance_node(node: Node):
    balance = get_balance(node)

    if balance > 1:
        if get_balance(node.left) < 0:
            node.left = left_rotate(node.left)
        return right_rotate(node)
    if balance < -1:
        if get_balance(node.right) > 0:
            node.right = right_rotate(node.right)
        return left_rotate(node)
    return node


class AVLTree(IAVLTree,Generic[K, V]):
    def __init__(self,list = []):
        self.root = None
        for key, value in list:
            self.insert(key, value)
    
    def insert(self, key: K, value: V) -> None:
        def _insert(node: Node, key: K, value: V) -> Node:
            #This is where it finds a valid spot to insert the new ndoe
            if node is None:
                return Node(key, value)
            
            #this is it navigating to a valid spot to insert the new node
            #additionally its caring about the node.left or right in order to updates heights to rebalance the tree
            if key < node.key:
                node.left = _insert(node.left, key, value)
            elif key > node.key:
                node.right = _insert(node.right, key, value)
            else:
                raise KeyError("Duplicate entry")
            
            #This updates the height of the node, height might have changed within the recursion and this is hit after under it is recursed
            node.height = 1 + max(height(node.left), height(node.right))

            return balance_node(node)
        self.root = _insert(self.root, key, value)



    def search(self, key: K) -> Optional[V]:
        def _search(root: Node, key: K)-> Optional[V]:
            if root is None or root.key == key:
                return root
            if root.key < key:
                return _search(root.right, key)
            return _search(root.left, key)
        return _search(self.root, key)



    def delete(self, key: K) -> None:
        """Deletes a key and its associated value from the binary search tree.

        Args:
            key (K): The key to delete.

        Raises:
            KeyError: If the key is not present in the tree.
        """
        def _delete(root: Node, key: K):

            #will only recurse down to this point if the key is not in the tree
            if root is None:
                raise KeyError("Key not found in the tree.")

            #this is where it recurses down the tree to find the node to delete
            if key < root.key:
                root.left = _delete(root.left, key)
            elif key > root.key:
                root.right = _delete(root.right, key)
            
            #This activates when the key is found
            else:
                #if there is no left child then the found nodes right child takes its spot
                if root.left is None:  
                    return root.right
                #if it has a left child and no right child then the left child takes its spot
                #bc of balancing in both of these cases we don't have to worry about either of these two cases having children
                elif root.right is None:
                    return root.left

                #This is the case where it has two children, what we want to replace the node with the smallest node greater than the found node
                #We do this to preserve its structure and balance
                #finding the smallest node greater than the found node
                temp = leftmost(root.right)

                #replaces the found node with the proper node, while preserving its children
                root.key = temp.key
                root.value = temp.value
                #runs down and deletes the node that now resides within the found nodes spot 
                root.right = _delete(root.right, temp.key)

            # This code only runs when its recursing back up. The heights and balances through this process 
            root.height = 1 + max(height(root.left), height(root.right))

            #Finds the balance of the current node 
            balance = get_balance(root)
            root.height = 1 + max(height(root.left), height(root.right))

            return balance_node(root)

        def leftmost(root):
            while root.left is not None:
                root = root.left
            return root

        self.root = _delete(self.root, key)

    def delete_with_value(self, key: K, value: V) -> None:
        def _delete(root: Node, key: K, value: V):

            #will only recurse down to this point if the key is not in the tree
            if root is None:
                raise KeyError("Key not found in the tree.")

            #this is where it recurses down the tree to find the node to delete
            if key < root.key:
                root.left = _delete(root.left, key, value)
            elif key > root.key:
                root.right = _delete(root.right, key, value)
            
            #This activates when the key is found
            else:
                if root.value != value:
                    if root.value < value:
                        root.right = _delete(root.right, key, value)
                    else:
                        root.left = _delete(root.left, key, value)
                #if there is no left child then the found nodes right child takes its spot
                if root.left is None:  
                    return root.right
                #if it has a left child and no right child then the left child takes its spot
                #bc of balancing in both of these cases we don't have to worry about either of these two cases having children
                elif root.right is None:
                    return root.left

                #This is the case where it has two children, what we want to replace the node with the smallest node greater than the found node
                #We do this to preserve its structure and balance
                #finding the smallest node greater than the found node
                temp = leftmost(root.right)

                #replaces the found node with the proper node, while preserving its children
                root.key = temp.key
                root.value = temp.value
                #runs down and deletes the node that now resides within the found nodes spot 
                root.right = _delete(root.right, temp.key, temp.value)

            # This code only runs when its recursing back up. The heights and balances through this process 
            root.height = 1 + max(height(root.left), height(root.right))

            #Finds the balance of the current node 
            balance = get_balance(root)
            root.height = 1 + max(height(root.left), height(root.right))

            return balance_node(root)

        def leftmost(root):
            while root.left is not None:
                root = root.left
            return root

        self.root = _delete(self.root, key, value)


    def inorder(self, visit: Optional[Callable[[V], None]]=None) -> List[K]:
        """Returns the inorder traversal of the binary search tree, containing the keys in sorted order.

        Args:
            visit (Optional[Callable[[V], None]]): A function to call on each value during the traversal.        
        
        Returns:
            List[K]: The list of keys in inorder traversal.
        """
        def _inorder(root, keys):
            if root is None:
                return None
            _inorder(root.left, keys)
            keys.append(root)
            _inorder(root.right, keys)
            return keys
        return _inorder(self.root, [])

    def preorder(self, visit: Optional[Callable[[V], None]]=None) -> List[K]:
        """Returns the preorder traversal of the binary search tree.

        Args:
            visit (Optional[Callable[[V], None]]): A function to call on each value during the traversal.        
        
        Returns:
            List[K]: The list of keys in preorder traversal.
        """
        def _preorder(root, keys):
            if root is None:
                return None
            keys.append(root.key)
            _preorder(root.left, keys)
            _preorder(root.right, keys)
            return keys
        return _preorder(self.root, [])

    def postorder(self, visit: Optional[Callable[[V], None]]=None) -> List[K]:
        """Returns the postorder traversal of the binary search tree.

        Returns:
            List[K]: The list of keys in postorder traversal.
        """
        order = []
        def visit(node):
            order.append(node.key)
        
        def _postorder(root):
            if root is None:
                return None
            _postorder(root.left)
            _postorder(root.right)
            visit(root)
        
        _postorder(self.root)
        return order

    def bforder(self, visit: Optional[Callable[[V], None]] = None) -> List[K]:
        """Returns the keys in the binary search tree in breadth-first order.

        Args:
            visit (Optional[Callable[[V], None]]): A function to call on each value during the traversal.        
        
        Returns:
            List[K]: The list of keys in breadth-first order.
        """
        if not self.root:
            return []

        keys = []
        queue = deque([self.root])  # Initialize the deque with the root node.

        while queue:
            current = queue.popleft()  # Remove and return the leftmost node.
            keys.append(current.key)  # Add the current node's key to the list.

            # Add the left and right children to the queue if they exist.
            if current.left:
                queue.append(current.left)
            if current.right:
                queue.append(current.right)

        return keys

    def size(self) -> int:
        def _size(root):
            #Base case for recursion
            if root is None:
                return 0
            #recursive case 
            return 1 + _size(root.left) + _size(root.right)
        return _size(self.root)
    
    def __len__(self) -> int:
        return self.size()
    
    def __contains__(self, key: K) -> bool:
        return self.search(key) is not None
    
    def __str__(self) -> str:
        """Returns a string representation of the AVL tree."""
        if not self.root:
            return "<empty tree>"

        def _str(node: Optional[Node], depth: int = 0) -> str:
            if node is None:
                return ""
            left_str = _str(node.left, depth + 1)
            right_str = _str(node.right, depth + 1)
            node_str = " " * (4 * depth) + f"{node.key}: {node.value} (h={node.height})\n"
            return left_str + node_str + right_str

        return _str(self.root)
    
    def is_empty(self) -> bool:
        return self.root is None


    def nodes_less_than(self, n: K) -> List[K]:
        """Returns all keys that are less than n."""
        result = []

        def _nodes_less_than(node: Optional[Node]):
            if node is None:
                return
            
            if node.key <= n:
                # Collect the key if it's less than n
                result.append(node)
                # Traverse the left subtree
                _nodes_less_than(node.left)
                # Traverse the right subtree
                _nodes_less_than(node.right)
            else:
                # Only traverse the left subtree if node.key >= n
                _nodes_less_than(node.left)

        _nodes_less_than(self.root)
        return result
    
    def nodes_greater_than(self, n: K) -> List[K]:
        """Returns all keys that are greater than n."""
        result = []

        def _nodes_greater_than(node: Optional[Node]):
            if node is None:
                return
            
            if node.key >= n:
                # Collect the key if it's greater than n
                result.append(node)
                # Traverse the left subtree
                _nodes_greater_than(node.left)
                # Traverse the right subtree
                _nodes_greater_than(node.right)
            else:
                # Only traverse the right subtree if node.key <= n
                _nodes_greater_than(node.right)

        _nodes_greater_than(self.root)
        return result
    
    def check_balance(self) -> bool:
        def _check_balance(node: Optional[Node]) -> bool:
            if node is None:
                return True
            return abs(get_balance(node)) < 2 and _check_balance(node.left) and _check_balance(node.right)
        
        return _check_balance(self.root)
    
    def max_key(self) -> K:
        def _max_key(node: Optional[Node]) -> K:
            if node.right is None:
                return node.key
            return _max_key(node.right)
        
        return _max_key(self.root)
