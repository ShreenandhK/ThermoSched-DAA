import itertools
import unittest

from thermosched.knapsack import fractional_knapsack, greedy_whole_jobs, knapsack_01
from thermosched.models import Job, random_jobs

SAMPLE = [Job("J1", 60, 10), Job("J2", 100, 20), Job("J3", 120, 30), Job("J4", 90, 25), Job("J5", 30, 15)]


def brute_force(jobs, budget):
    """Try every subset - only for checking small inputs."""
    best = 0
    for r in range(len(jobs) + 1):
        for subset in itertools.combinations(jobs, r):
            if sum(j.thermal_cost for j in subset) <= budget:
                best = max(best, sum(j.benefit for j in subset))
    return best


class NormalCases(unittest.TestCase):
    def test_01_sample(self):
        r = knapsack_01(SAMPLE, 50)
        self.assertEqual(r["benefit"], 220)
        self.assertEqual([j.name for j in r["chosen"]], ["J2", "J3"])

    def test_fractional_sample(self):
        r = fractional_knapsack(SAMPLE, 50)
        self.assertAlmostEqual(r["benefit"], 240.0)
        self.assertAlmostEqual(r["used"], 50.0)

    def test_greedy_is_not_optimal_for_whole_jobs(self):
        self.assertEqual(greedy_whole_jobs(SAMPLE, 50)["benefit"], 190)


class BoundaryCases(unittest.TestCase):
    def test_zero_budget(self):
        self.assertEqual(knapsack_01(SAMPLE, 0)["benefit"], 0)
        self.assertEqual(fractional_knapsack(SAMPLE, 0)["benefit"], 0)

    def test_no_jobs(self):
        self.assertEqual(knapsack_01([], 10)["benefit"], 0)
        self.assertEqual(fractional_knapsack([], 10)["benefit"], 0)

    def test_job_heavier_than_budget(self):
        jobs = [Job("big", 500, 100)]
        self.assertEqual(knapsack_01(jobs, 50)["benefit"], 0)
        self.assertAlmostEqual(fractional_knapsack(jobs, 50)["benefit"], 250.0)   # half of it

    def test_exact_fit(self):
        self.assertEqual(knapsack_01(SAMPLE, 100)["benefit"], 400)   # every job fits exactly


class LargeCases(unittest.TestCase):
    def test_large_instance_bounds(self):
        jobs = random_jobs(200, max_cost=50, seed=42)
        dp = knapsack_01(jobs, 2000)
        self.assertLessEqual(dp["used"], 2000)
        self.assertEqual(sum(j.benefit for j in dp["chosen"]), dp["benefit"])
        # fractional is an upper bound for 0/1; greedy is a lower bound
        self.assertGreaterEqual(fractional_knapsack(jobs, 2000)["benefit"] + 1e-9, dp["benefit"])
        self.assertLessEqual(greedy_whole_jobs(jobs, 2000)["benefit"], dp["benefit"])


class DifficultCases(unittest.TestCase):
    def test_matches_brute_force_on_random_small_instances(self):
        for seed in range(150):
            jobs = random_jobs(9, max_cost=20, seed=seed)
            budget = sum(j.thermal_cost for j in jobs) // 2
            self.assertEqual(knapsack_01(jobs, budget)["benefit"], brute_force(jobs, budget), f"seed {seed}")

    def test_equal_ratios(self):
        jobs = [Job("a", 10, 5), Job("b", 20, 10), Job("c", 30, 15)]   # every ratio is 2
        self.assertEqual(knapsack_01(jobs, 20)["benefit"], 40)
        self.assertAlmostEqual(fractional_knapsack(jobs, 20)["benefit"], 40.0)


if __name__ == "__main__":
    unittest.main()
