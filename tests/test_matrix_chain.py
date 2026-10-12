import random
import unittest
from functools import lru_cache

from thermosched.matrix_chain import left_to_right_cost, matrix_chain_order


def brute_force(dims):
    """Try every bracketing recursively - only for checking small chains."""
    @lru_cache(maxsize=None)
    def best(i, j):
        if i == j:
            return 0
        return min(best(i, k) + best(k + 1, j) + dims[i - 1] * dims[k] * dims[j] for k in range(i, j))
    return best(1, len(dims) - 1)


class MatrixChainTests(unittest.TestCase):
    def test_normal_clrs_example(self):
        r = matrix_chain_order([30, 35, 15, 5, 10, 20, 25])
        self.assertEqual(r["optimal_cost"], 15125)
        self.assertEqual(r["order"], "((A1(A2A3))((A4A5)A6))")

    def test_normal_project_pipeline(self):
        r = matrix_chain_order([10, 30, 5, 60, 10])
        self.assertEqual(r["optimal_cost"], 5000)
        self.assertEqual(r["naive_cost"], 10500)
        self.assertEqual(r["order"], "((A1A2)(A3A4))")

    def test_boundary_single_matrix(self):
        self.assertEqual(matrix_chain_order([4, 7])["optimal_cost"], 0)

    def test_boundary_two_matrices(self):
        r = matrix_chain_order([4, 7, 3])
        self.assertEqual(r["optimal_cost"], 4 * 7 * 3)
        self.assertEqual(r["optimal_cost"], left_to_right_cost([4, 7, 3]))

    def test_difficult_matches_brute_force(self):
        rng = random.Random(5)
        for _ in range(100):
            dims = [rng.randint(1, 50) for _ in range(rng.randint(2, 9))]
            self.assertEqual(matrix_chain_order(dims)["optimal_cost"], brute_force(tuple(dims)))

    def test_large_chain_never_worse_than_naive(self):
        rng = random.Random(9)
        dims = [rng.randint(5, 100) for _ in range(101)]
        r = matrix_chain_order(dims)
        self.assertLessEqual(r["optimal_cost"], r["naive_cost"])
        self.assertEqual(r["dp_steps"], (100 ** 3 - 100) // 6)     # exact n^3 growth


if __name__ == "__main__":
    unittest.main()
