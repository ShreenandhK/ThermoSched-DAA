"""Module 4a: Binomial Heap (min-heap) for dynamic job priority.

A binomial heap is a list of binomial trees with distinct degrees (like the 1-bits of n).
Smaller key = more urgent job.

Operation       Time (worst case)
insert          O(log n)
find-min        O(log n)
extract-min     O(log n)
decrease-key    O(log n)   (bubble the key up the tree)
merge           O(log n)

self.ops counts basic steps so both heaps can be compared fairly:
+1 per key comparison and +1 per pointer change (link, swap, child promoted to root).
"""


class BinomialNode:
    def __init__(self, key, item):
        self.key = key
        self.item = item
        self.parent = None
        self.children = []

    @property
    def degree(self):
        return len(self.children)


class BinomialHeap:
    def __init__(self):
        self.roots = []        # roots of the binomial trees
        self.node_of = {}      # item -> node, so decrease_key can find a job directly
        self.size = 0
        self.ops = 0

    def __len__(self):
        return self.size

    def _link(self, a, b):
        """Join two trees of equal degree: the larger root becomes a child of the smaller. O(1)."""
        self.ops += 2                              # one comparison + one link
        if b.key < a.key:
            a, b = b, a
        b.parent = a
        a.children.append(b)
        return a

    def _consolidate(self, roots):
        """Combine trees until every degree appears once (like adding binary numbers). O(log n)."""
        by_degree = {}
        for node in roots:
            while node.degree in by_degree:
                node = self._link(node, by_degree.pop(node.degree))
            by_degree[node.degree] = node
        self.roots = [by_degree[d] for d in sorted(by_degree)]

    def insert(self, key, item):
        node = BinomialNode(key, item)
        self.node_of[item] = node
        self.size += 1
        self._consolidate(self.roots + [node])

    def _min_root(self):
        best = self.roots[0]
        for node in self.roots[1:]:
            self.ops += 1
            if node.key < best.key:
                best = node
        return best

    def find_min(self):
        node = self._min_root()
        return node.key, node.item

    def extract_min(self):
        """Remove the most urgent job. Its children become trees of their own."""
        if self.size == 0:
            raise IndexError("extract_min from an empty heap")
        best = self._min_root()
        self.roots.remove(best)
        for child in best.children:
            child.parent = None
            self.ops += 1                          # child promoted to root
        self._consolidate(self.roots + best.children)
        del self.node_of[best.item]
        self.size -= 1
        return best.key, best.item

    def decrease_key(self, item, new_key):
        """Make a job more urgent: swap it upward while it is smaller than its parent. O(log n)."""
        node = self.node_of[item]
        if new_key > node.key:
            raise ValueError("new key is larger than current key")
        node.key = new_key
        while node.parent is not None:
            self.ops += 1                          # compare with parent
            if node.key >= node.parent.key:
                break
            self.ops += 1                          # swap with parent
            parent = node.parent
            node.key, parent.key = parent.key, node.key
            node.item, parent.item = parent.item, node.item
            self.node_of[node.item] = node
            self.node_of[parent.item] = parent
            node = parent

    def merge(self, other):
        """Union of two heaps (e.g. two CPU queues combined). O(log n)."""
        self.node_of.update(other.node_of)
        self.size += other.size
        self._consolidate(self.roots + other.roots)
