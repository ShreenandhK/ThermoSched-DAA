"""Module 4b: Fibonacci Heap (min-heap) for dynamic job priority.

Fibonacci heaps are "lazy": insert and decrease-key do almost no work, and the tidying up
(consolidation) is delayed until extract-min.

Operation       Time (amortized)
insert          O(1)
find-min        O(1)
extract-min     O(log n)
decrease-key    O(1)        <- the reason to prefer it when priorities change often
merge           O(1)

Note: Python lists are used for the root list and child lists to keep the code readable.
self.ops counts +1 per key comparison and +1 per pointer change (link, cut, root add).
A textbook implementation uses circular doubly linked lists so that merge and cut are O(1).
"""


class FibNode:
    def __init__(self, key, item):
        self.key = key
        self.item = item
        self.parent = None
        self.children = []
        self.mark = False      # True if this node already lost a child since becoming a child

    @property
    def degree(self):
        return len(self.children)


class FibonacciHeap:
    def __init__(self):
        self.roots = []
        self.min = None
        self.node_of = {}
        self.size = 0
        self.ops = 0

    def __len__(self):
        return self.size

    def _add_root(self, node):
        node.parent = None
        node.mark = False
        self.roots.append(node)
        self.ops += 2                              # one pointer change + one comparison with min
        if self.min is None or node.key < self.min.key:
            self.min = node

    def insert(self, key, item):
        """Just add a one-node tree to the root list. O(1)."""
        node = FibNode(key, item)
        self.node_of[item] = node
        self.size += 1
        self._add_root(node)

    def find_min(self):
        return self.min.key, self.min.item

    def extract_min(self):
        """Remove the minimum, promote its children, then consolidate. O(log n) amortized."""
        if self.size == 0:
            raise IndexError("extract_min from an empty heap")
        best = self.min
        self.roots.remove(best)
        for child in best.children:
            self._add_root(child)
        self._consolidate()
        del self.node_of[best.item]
        self.size -= 1
        return best.key, best.item

    def _consolidate(self):
        """Link roots of equal degree until all degrees differ, then find the new minimum."""
        by_degree = {}
        for node in self.roots:
            while node.degree in by_degree:
                other = by_degree.pop(node.degree)
                self.ops += 2                      # one comparison + one link
                if other.key < node.key:
                    node, other = other, node
                other.parent = node             # link: other becomes child of node
                other.mark = False
                node.children.append(other)
            by_degree[node.degree] = node
        self.roots = list(by_degree.values())
        self.min = None
        for node in self.roots:
            self.ops += 1
            if self.min is None or node.key < self.min.key:
                self.min = node

    def decrease_key(self, item, new_key):
        """Lower a key. If heap order breaks, cut the node to the root list. O(1) amortized."""
        node = self.node_of[item]
        if new_key > node.key:
            raise ValueError("new key is larger than current key")
        node.key = new_key
        parent = node.parent
        if parent is not None:
            self.ops += 1                          # compare with parent
        if parent is not None and node.key < parent.key:
            self._cut(node, parent)
            self._cascading_cut(parent)
        self.ops += 1                              # compare with min
        if node.key < self.min.key:
            self.min = node

    def _cut(self, node, parent):
        parent.children.remove(node)
        self._add_root(node)                       # _add_root counts the pointer change

    def _cascading_cut(self, node):
        """A parent that loses a second child is cut too - this keeps trees bushy (degree O(log n))."""
        parent = node.parent
        if parent is not None:
            if not node.mark:
                node.mark = True
            else:
                self._cut(node, parent)
                self._cascading_cut(parent)

    def merge(self, other):
        """Concatenate root lists. O(1) with linked lists."""
        self.roots.extend(other.roots)
        self.node_of.update(other.node_of)
        self.size += other.size
        if other.min is not None and (self.min is None or other.min.key < self.min.key):
            self.min = other.min
