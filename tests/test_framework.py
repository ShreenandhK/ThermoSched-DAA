import os
import unittest

from thermosched.framework import decide_computation_order, decide_job_admission, run_scenario
from thermosched.models import Job, load_scenario

HERE = os.path.dirname(os.path.abspath(__file__))
PEAK = load_scenario(os.path.join(HERE, "..", "scenarios", "peak_hours.json"))
NIGHT = load_scenario(os.path.join(HERE, "..", "scenarios", "night_batch.json"))


class AdaptationTests(unittest.TestCase):
    """The framework must pick different techniques when scenario properties change."""

    @classmethod
    def setUpClass(cls):
        cls.peak = {d["module"]: d for d in run_scenario(PEAK)["decisions"]}
        cls.night = {d["module"]: d for d in run_scenario(NIGHT)["decisions"]}

    def test_admission_changes_with_divisibility(self):
        self.assertTrue(self.peak["Job admission"]["technique"].startswith("0/1 Knapsack"))
        self.assertTrue(self.night["Job admission"]["technique"].startswith("Fractional Knapsack"))
        self.assertEqual(self.peak["Job admission"]["measure"]["benefit"], 220)
        self.assertAlmostEqual(self.night["Job admission"]["measure"]["benefit"], 240.0)

    def test_matrix_chain_only_when_useful(self):
        self.assertTrue(self.peak["Computation reduction"]["technique"].startswith("Matrix Chain"))
        self.assertTrue(self.night["Computation reduction"]["technique"].startswith("Direct"))

    def test_heap_changes_with_update_pattern(self):
        self.assertEqual(self.peak["Dynamic job priority"]["technique"], "Fibonacci Heap")
        self.assertEqual(self.night["Dynamic job priority"]["technique"], "Binomial Heap")

    def test_telemetry_always_uses_btree(self):
        for report in (self.peak, self.night):
            d = report["Telemetry index"]
            self.assertTrue(d["technique"].startswith("B-Tree"))
            self.assertEqual(d["measure"]["range_hits"], 120)   # 10 minutes of readings, one every 5 s

    def test_gcd_scaling_keeps_the_same_answer(self):
        scenario = {"jobs": [Job("a", 7, 30), Job("b", 9, 45), Job("c", 4, 15)],
                    "thermal_budget": 60, "jobs_divisible": False}
        d = decide_job_admission(scenario)
        self.assertEqual(d["measure"]["gcd_scale"], 15)
        self.assertEqual(d["measure"]["benefit"], 13)      # b + c (45 + 15 = 60)

    def test_boundary_single_matrix_pipeline(self):
        d = decide_computation_order({"matrix_pipeline": [8, 8]})
        self.assertTrue(d["technique"].startswith("Direct"))


if __name__ == "__main__":
    unittest.main()
