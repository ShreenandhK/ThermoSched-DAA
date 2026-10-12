import math
import random
import unittest

from thermosched.btree import BTree


def leaf_depths(node, depth, t, is_root, depths):
    """Collect leaf depths and check every node's key count and ordering."""
    assert len(node.keys) <= 2 * t - 1, "node over-full"
    assert is_root or len(node.keys) >= t - 1, "node under-full"
    assert node.keys == sorted(node.keys), "keys out of order"
    if node.leaf:
        depths.add(depth)
    else:
        assert len(node.children) == len(node.keys) + 1, "wrong number of children"
    for child in node.children:
        leaf_depths(child, depth + 1, t, False, depths)
    return depths


class BTreeTests(unittest.TestCase):
    def test_normal_insert_and_search(self):
        tree = BTree()
        for k in [50, 20, 70, 10, 30, 60, 80]:
            tree.insert(k, f"v{k}")
        self.assertEqual(tree.search(30)[0], "v30")
        self.assertIsNone(tree.search(35)[0])

    def test_boundary_empty_tree(self):
        tree = BTree()
        self.assertIsNone(tree.search(1)[0])
        self.assertEqual(tree.range_query(0, 100), [])
        self.assertEqual(tree.height(), 1)

    def test_boundary_root_split(self):
        """The 6th key overflows a t=3 root (max 5 keys): it splits and the tree grows one level."""
        tree = BTree(t=3)
        for k in range(5):
            tree.insert(k, k)
        self.assertEqual((tree.height(), tree.splits), (1, 0))
        tree.insert(5, 5)
        self.assertEqual((tree.height(), tree.splits), (2, 1))
        self.assertEqual(tree.root.keys, [2])

    def test_range_query_matches_sorted_list(self):
        rng = random.Random(4)
        keys = rng.sample(range(100000), 3000)
        tree = BTree()
        for k in keys:
            tree.insert(k, k)
        expected = sorted(k for k in keys if 20000 <= k <= 40000)
        self.assertEqual([k for k, _ in tree.range_query(20000, 40000)], expected)

    def test_difficult_sorted_inserts_stay_balanced(self):
        """Time-ordered telemetry is the worst case for an unbalanced BST."""
        n = 20000
        tree = BTree(t=3)
        for k in range(n):
            tree.insert(k, k)
        self.assertEqual(len(leaf_depths(tree.root, 1, 3, True, set())), 1)   # all leaves at the same depth
        self.assertLessEqual(tree.height(), math.log((n + 1) / 2, 3) + 1)

    def test_large_random_inserts_keep_invariants(self):
        rng = random.Random(8)
        keys = rng.sample(range(10 ** 6), 30000)
        tree = BTree(t=4)
        for k in keys:
            tree.insert(k, k)
        leaf_depths(tree.root, 1, 4, True, set())
        for k in keys[:500]:
            self.assertEqual(tree.search(k)[0], k)


if __name__ == "__main__":
    unittest.main()
