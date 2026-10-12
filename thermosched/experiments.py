"""Experiments: run each technique on growing inputs and compare measurements with theory.

Every experiment returns a list of rows (dicts). main.py saves them to results/*.csv
and to dashboard/data.js.
"""

import math
import random
import tracemalloc
from time import perf_counter

from .binomial_heap import BinomialHeap
from .btree import BTree
from .fibonacci_heap import FibonacciHeap
from .knapsack import fractional_knapsack, greedy_whole_jobs, knapsack_01
from .matrix_chain import matrix_chain_order
from .models import random_jobs
from .workloads import priority_workload, telemetry_workload


def ms(fn, *args, repeats=3):
    """Run fn several times and keep the fastest time (removes noise from other programs)."""
    best = float("inf")
    for _ in range(repeats):
        start = perf_counter()
        result = fn(*args)
        best = min(best, perf_counter() - start)
    return result, round(best * 1000, 3)


def peak_kib(fn, *args):
    """Peak extra memory used while fn runs (tracemalloc), in KiB."""
    tracemalloc.start()
    fn(*args)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return round(peak / 1024, 1)


def knapsack_scaling():
    """0/1 DP grows with n*W; fractional greedy grows with n log n only."""
    rows = []
    for n in (25, 50, 100, 200):
        for budget in (100, 1000, 5000):
            jobs = random_jobs(n, max_cost=budget // 4 or 1, seed=n)
            dp, dp_ms = ms(knapsack_01, jobs, budget)
            fr, fr_ms = ms(fractional_knapsack, jobs, budget)
            rows.append({
                "n": n, "W": budget, "dp_cells": dp["cells"],
                "dp_ms": dp_ms, "dp_peak_kib": peak_kib(knapsack_01, jobs, budget),
                "frac_ms": fr_ms, "dp_benefit": dp["benefit"], "frac_benefit": round(fr["benefit"], 1),
            })
    return rows


def knapsack_quality(trials=300):
    """Difficult instances: how often is greedy wrong for indivisible jobs?"""
    rows = []
    for n in (5, 10, 20, 40):
        wrong, gap_total = 0, 0.0
        for t in range(trials):
            jobs = random_jobs(n, max_cost=40, seed=1000 * n + t)
            budget = sum(j.thermal_cost for j in jobs) // 2
            best = knapsack_01(jobs, budget)["benefit"]
            greedy = greedy_whole_jobs(jobs, budget)["benefit"]
            if greedy < best:
                wrong += 1
                gap_total += (best - greedy) / best
        rows.append({"n": n, "trials": trials, "greedy_wrong_pct": round(100 * wrong / trials, 1),
                     "avg_gap_when_wrong_pct": round(100 * gap_total / wrong, 2) if wrong else 0.0})
    return rows


def matrix_chain_scaling():
    """DP work grows as n^3; savings over left-to-right order on random chains."""
    rows = []
    rng = random.Random(3)
    for n in (5, 10, 20, 40, 80, 160):
        dims = [rng.randint(5, 100) for _ in range(n + 1)]
        r, t = ms(matrix_chain_order, dims)
        rows.append({"n": n, "dp_steps": r["dp_steps"], "dp_ms": t,
                     "naive_cost": r["naive_cost"], "optimal_cost": r["optimal_cost"],
                     "saved_pct": round(100 * (1 - r["optimal_cost"] / r["naive_cost"]), 1)})
    return rows


def heap_comparison():
    """Same run-queue workload on both heaps; vary size and the kind of priority update."""
    rows = []
    for n in (1000, 5000, 20000):
        for updates, kind in ((0, "none"), (4, "aging"), (1, "boost"), (4, "boost")):
            b = priority_workload(BinomialHeap, n, updates, kind)
            f = priority_workload(FibonacciHeap, n, updates, kind)
            rows.append({"n": n, "updates_per_dispatch": updates, "update_kind": kind,
                         "binomial_ops": b["ops"], "fibonacci_ops": f["ops"],
                         "binomial_ms": round(b["time_ms"], 1), "fibonacci_ms": round(f["time_ms"], 1)})
    return rows


def btree_scaling():
    """Telemetry index: height, node visits and comparisons per search as n grows (B-Tree, t = 3)."""
    rows = []
    for n in (1000, 10000, 50000):
        b = telemetry_workload(BTree, n, 2000)
        rows.append({"n": n, "height": b["height"],
                     "height_bound": round(math.log((n + 1) / 2, 3) + 1, 2),   # log_t((n+1)/2) + 1 levels
                     "nodes_visited": round(b["avg_nodes_visited"], 2),
                     "comparisons": round(b["avg_comparisons"], 2),
                     "splits": b["splits"], "insert_ms": round(b["insert_ms"], 1)})
    return rows


def run_all():
    return {
        "knapsack_scaling": knapsack_scaling(),
        "knapsack_quality": knapsack_quality(),
        "matrix_chain_scaling": matrix_chain_scaling(),
        "heap_comparison": heap_comparison(),
        "btree_scaling": btree_scaling(),
    }
