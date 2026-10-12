"""Real-world entities of the scenario: CPU jobs and the scenario file that describes a server's workload."""

import json
import random
from dataclasses import dataclass


@dataclass
class Job:
    """One CPU job waiting to be admitted.

    benefit      -> useful output delivered if the job runs (knapsack "value")
    thermal_cost -> CPU load / heat the job adds (knapsack "weight")
    """
    name: str
    benefit: int
    thermal_cost: int

    @property
    def ratio(self):
        """Benefit per unit of heat. Used by the greedy (fractional) strategy."""
        return self.benefit / self.thermal_cost


def load_scenario(path):
    """Read a scenario JSON file and turn its job list into Job objects."""
    with open(path, encoding="utf-8") as f:
        scenario = json.load(f)
    scenario["jobs"] = [Job(j["name"], j["benefit"], j["thermal_cost"]) for j in scenario["jobs"]]
    for job in scenario["jobs"]:
        if job.thermal_cost <= 0 or job.benefit < 0:
            raise ValueError(f"{job.name}: thermal_cost must be > 0 and benefit >= 0")
    return scenario


def random_jobs(n, max_cost=30, max_benefit=100, seed=1):
    """Generate n random jobs (used by experiments and tests)."""
    rng = random.Random(seed)
    return [Job(f"J{i + 1}", rng.randint(1, max_benefit), rng.randint(1, max_cost)) for i in range(n)]
