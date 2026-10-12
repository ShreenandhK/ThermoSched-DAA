"""Module 5a: B-Tree index for historical thermal telemetry (key = timestamp).

Every node holds between t-1 and 2t-1 keys (t = minimum degree), so the tree is short and wide.
That means few node visits per search - ideal when each node is one disk block.

Operation       Time                 Space
search          O(t * log_t n)       O(n) for the tree
insert          O(t * log_t n)
range query     O(t * log_t n + k)   (k = records returned)

Telemetry is an append-only log, so deletion is not needed in this framework.
"""


class BTreeNode:
    def __init__(self, leaf=True):
        self.keys = []
        self.values = []
        self.children = []
        self.leaf = leaf


class BTree:
    def __init__(self, t=3):
        self.t = t
        self.root = BTreeNode()
        self.comparisons = 0   # key comparisons
        self.splits = 0        # node splits (structural work)
        self.size = 0

    def search(self, key):
        """Return (value, nodes_visited) or (None, nodes_visited)."""
        node, visited = self.root, 0
        while True:
            visited += 1
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                self.comparisons += 1
                i += 1
            self.comparisons += 1
            if i < len(node.keys) and key == node.keys[i]:
                return node.values[i], visited
            if node.leaf:
                return None, visited
            node = node.children[i]

    def insert(self, key, value):
        """CLRS single-pass insert: split full nodes on the way down so there is always room."""
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
        self._insert_non_full(self.root, key, value)
        self.size += 1

    def _split_child(self, parent, i):
        """Split the full child parent.children[i] into two nodes; its middle key moves up."""
        self.splits += 1
        t = self.t
        full = parent.children[i]
        right = BTreeNode(leaf=full.leaf)
        parent.keys.insert(i, full.keys[t - 1])
        parent.values.insert(i, full.values[t - 1])
        parent.children.insert(i + 1, right)
        right.keys, full.keys = full.keys[t:], full.keys[:t - 1]
        right.values, full.values = full.values[t:], full.values[:t - 1]
        if not full.leaf:
            right.children, full.children = full.children[t:], full.children[:t]

    def _insert_non_full(self, node, key, value):
        while True:
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                self.comparisons += 1
                i -= 1
            i += 1
            if node.leaf:
                node.keys.insert(i, key)
                node.values.insert(i, value)
                return
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                self.comparisons += 1
                if key > node.keys[i]:
                    i += 1
            node = node.children[i]

    def range_query(self, low, high):
        """All (key, value) with low <= key <= high, in key order."""
        out = []
        self._range(self.root, low, high, out)
        return out

    def _range(self, node, low, high, out):
        for i, key in enumerate(node.keys):
            if not node.leaf and low < key:
                self._range(node.children[i], low, high, out)
            if low <= key <= high:
                out.append((key, node.values[i]))
            if key > high:
                return
        if not node.leaf:
            self._range(node.children[-1], low, high, out)

    def height(self):
        h, node = 1, self.root
        while not node.leaf:
            node = node.children[0]
            h += 1
        return h
