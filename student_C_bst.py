
"""V3: Pointer-based Binary Search Tree index for Problem 18."""


class BSTNode:
    """One BST node stores one key and pointers to two children."""

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BSTIndex:
    """Unbalanced BST supporting insert, search, range_query, and height."""

    def __init__(self):
        self.root = None

    def insert(self, key):
        """Insert a key. Duplicate keys are ignored."""
        if self.root is None:
            self.root = BSTNode(key)
            return

        node = self.root
        while True:
            if key == node.key:
                return

            side = 'left' if key < node.key else 'right'
            child = getattr(node, side)

            if child is None:
                setattr(node, side, BSTNode(key))
                return

            node = child

    def search(self, key):
        """Return True if key exists, otherwise False."""
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def range_query(self, low, high):
        """Return all keys in inclusive range [low, high]."""
        result = []
        stack = []
        node = self.root

        while stack or node:
            while node:
                stack.append(node)
                node = node.left

            node = stack.pop()
            if low <= node.key <= high:
                result.append(node.key)
            if node.key > high:
                break
            node = node.right

        return result

    def height(self):
        """Return maximum root-to-leaf edge count."""
        if self.root is None:
            return -1

        level = -1
        frontier = [self.root]
        while frontier:
            level += 1
            frontier = [
                child
                for current in frontier
                for child in (current.left, current.right)
                if child is not None
            ]
        return level

    def inorder(self):
        """Return every key in ascending order."""
        result = []
        stack = []
        node = self.root
        while stack or node:
            while node:
                stack.append(node)
                node = node.left
            node = stack.pop()
            result.append(node.key)
            node = node.right
        return result


# Interactive terminal
bst = BSTIndex()

while True:
    command = input("BST> ").split()

    if not command:
        continue

    if command[0] == "insert" and len(command) == 2:
        bst.insert(int(command[1]))
        print("Inserted")

    elif command[0] == "search" and len(command) == 2:
        print(bst.search(int(command[1])))

    elif command[0] == "range" and len(command) == 3:
        print(bst.range_query(int(command[1]), int(command[2])))

    elif command[0] == "height":
        print(bst.height())

    elif command[0] == "inorder":
        print(bst.inorder())

    elif command[0] == "exit":
        break

    else:
        print("Invalid command")

