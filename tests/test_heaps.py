import random
import unittest

from thermosched.binomial_heap import BinomialHeap
from thermosched.fibonacci_heap import FibonacciHeap

HEAPS = (BinomialHeap, FibonacciHeap)


class HeapTests(unittest.TestCase):
    def test_normal_sorted_output(self):
        for cls in HEAPS:
            h = cls()
            keys = [5, 3, 9, 1, 7, 2]
            for i, k in enumerate(keys):
                h.insert(k, i)
            self.assertEqual([h.extract_min()[0] for _ in keys], sorted(keys), cls.__name__)

    def test_decrease_key_moves_job_to_front(self):
        for cls in HEAPS:
            h = cls()
            for i in range(50):
                h.insert(100 + i, i)
            h.decrease_key(42, 1)
            self.assertEqual(h.find_min(), (1, 42), cls.__name__)

    def test_merge(self):
        for cls in HEAPS:
            a, b = cls(), cls()
            for i in range(10):
                a.insert(i * 2, f"a{i}")
                b.insert(i * 2 + 1, f"b{i}")
            a.merge(b)
            self.assertEqual(len(a), 20)
            self.assertEqual([a.extract_min()[0] for _ in range(20)], list(range(20)), cls.__name__)

    def test_boundary_empty_and_single(self):
        for cls in HEAPS:
            h = cls()
            with self.assertRaises(IndexError):
                h.extract_min()
            h.insert(7, "only")
            self.assertEqual(h.extract_min(), (7, "only"))
            self.assertEqual(len(h), 0)

    def test_boundary_increase_key_rejected(self):
        for cls in HEAPS:
            h = cls()
            h.insert(5, "x")
            with self.assertRaises(ValueError):
                h.decrease_key("x", 10)

    def test_difficult_random_mixed_operations(self):
        """Random inserts / decrease-keys / extracts, checked against a plain dict."""
        for cls in HEAPS:
            rng = random.Random(1)
            h, current, next_id = cls(), {}, 0
            for _ in range(3000):
                op = rng.random()
                if op < 0.45 or not current:
                    current[next_id] = rng.randint(0, 10_000)
                    h.insert(current[next_id], next_id)
                    next_id += 1
                elif op < 0.75:
                    item = rng.choice(list(current))
                    current[item] -= rng.randint(0, 5_000)
                    h.decrease_key(item, current[item])
                else:
                    k, item = h.extract_min()
                    self.assertEqual(k, min(current.values()), cls.__name__)
                    del current[item]

    def test_large_heap_sort(self):
        rng = random.Random(2)
        keys = [rng.randint(0, 10 ** 6) for _ in range(20000)]
        for cls in HEAPS:
            h = cls()
            for i, k in enumerate(keys):
                h.insert(k, i)
            self.assertEqual([h.extract_min()[0] for _ in keys], sorted(keys), cls.__name__)


if __name__ == "__main__":
    unittest.main()
