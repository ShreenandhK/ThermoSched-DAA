"""The ThermoSched framework.

    SCENARIO -> MODEL -> DAA CHOICE -> EXECUTE -> MEASURE -> EXPLAIN

Each decide_* function looks at a PROPERTY of the scenario (never at an algorithm name),
picks a technique, runs it, runs the rejected alternative for comparison, and returns a
decision record that explains the choice. The telemetry index always uses a B-Tree;
build_telemetry_index explains why.
"""

import math
from time import perf_counter

from .binomial_heap import BinomialHeap
from .btree import BTree
from .fibonacci_heap import FibonacciHeap
from .knapsack import fractional_knapsack, greedy_whole_jobs, knapsack_01
from .matrix_chain import matrix_chain_order
from .models import Job
from .workloads import priority_workload, telemetry_workload


def timed(fn, *args):
    """Run fn(*args) and return (result, milliseconds)."""
    start = perf_counter()
    result = fn(*args)
    return result, (perf_counter() - start) * 1000


# ---------------------------------------------------------------- Module 1 + 2
def decide_job_admission(scenario):
    jobs, budget = scenario["jobs"], scenario["thermal_budget"]

    if scenario["jobs_divisible"]:
        # Property: CPU time can be split -> Fractional Knapsack (greedy) is optimal.
        result, ms = timed(fractional_knapsack, jobs, budget)
        alt, alt_ms = timed(knapsack_01, jobs, budget)
        return {
            "module": "Job admission",
            "property": "CPU time is divisible (jobs can receive a fraction of the budget)",
            "technique": "Fractional Knapsack (Greedy)",
            "complexity": "O(n log n) time, O(n) space",
            "rejected": "0/1 Knapsack DP",
            "reason": "With divisible items the highest benefit-per-heat job is always in an optimal "
                      "answer (greedy-choice property), so sorting by ratio is optimal and faster.",
            "result": f"benefit {result['benefit']:.1f}, budget used {result['used']:.1f}/{budget}",
            "detail": [(job.name, round(f, 3)) for job, f in result["shares"]],
            "measure": {"time_ms": ms, "benefit": result["benefit"],
                        "alt_benefit": alt["benefit"], "alt_time_ms": alt_ms},
        }

    # Property: jobs are indivisible -> 0/1 Knapsack DP.
    # Model step: divide all costs by their GCD - same answer, smaller DP table.
    g = math.gcd(budget, *[j.thermal_cost for j in jobs]) or 1
    scaled = [Job(j.name, j.benefit, j.thermal_cost // g) for j in jobs]
    result, ms = timed(knapsack_01, scaled, budget // g)
    chosen = [j for j in jobs if j.name in {c.name for c in result["chosen"]}]
    alt, alt_ms = timed(greedy_whole_jobs, jobs, budget)
    return {
        "module": "Job admission",
        "property": "jobs are indivisible (a job runs completely or not at all)",
        "technique": "0/1 Knapsack (Dynamic Programming)",
        "complexity": "O(n*W) time, O(n*W) space (pseudo-polynomial in W)",
        "rejected": "Greedy by benefit/heat ratio",
        "reason": "Greedy is not safe when jobs cannot be split; the DP compares the best answer "
                  "with and without every job, so it is always optimal.",
        "result": f"benefit {result['benefit']}, budget used {sum(j.thermal_cost for j in chosen)}/{budget}",
        "detail": [(j.name, 1) for j in chosen],
        "measure": {"time_ms": ms, "benefit": result["benefit"], "dp_cells": result["cells"],
                    "gcd_scale": g, "alt_benefit": alt["benefit"], "alt_time_ms": alt_ms},
    }


# ---------------------------------------------------------------- Module 3
def decide_computation_order(scenario):
    dims = scenario["matrix_pipeline"]
    if len(dims) - 1 < 3:
        # Property: 1 or 2 matrices -> only one possible order, nothing to optimise.
        return {
            "module": "Computation reduction",
            "property": f"chain of {len(dims) - 1} matrices",
            "technique": "Direct multiplication (no optimisation needed)",
            "complexity": "O(1) decision",
            "rejected": "Matrix Chain Multiplication DP",
            "reason": "With fewer than 3 matrices there is only one bracketing, so DP adds cost and no benefit.",
            "result": "single possible order",
            "detail": [],
            "measure": {},
        }
    result, ms = timed(matrix_chain_order, dims)
    saved = 100 * (1 - result["optimal_cost"] / result["naive_cost"])
    return {
        "module": "Computation reduction",
        "property": f"chain of {len(dims) - 1} matrices, dims {dims}",
        "technique": "Matrix Chain Multiplication (Dynamic Programming)",
        "complexity": "O(n^3) time, O(n^2) space",
        "rejected": "Left-to-right multiplication",
        "reason": "Bracketing does not change the result but changes the scalar multiplications "
                  "(our CPU-load proxy); DP finds the cheapest bracketing.",
        "result": f"{result['order']}: {result['optimal_cost']:,} mults vs {result['naive_cost']:,} "
                  f"left-to-right ({saved:.1f}% less work)",
        "detail": [],
        "measure": {"time_ms": ms, "optimal": result["optimal_cost"],
                    "naive": result["naive_cost"], "saved_pct": saved},
    }


# ---------------------------------------------------------------- Module 4
def decide_priority_queue(scenario):
    w = scenario["priority_workload"]
    jobs, updates, kind = w["jobs"], w["updates_per_dispatch"], w.get("update_kind", "aging")
    fib = priority_workload(FibonacciHeap, jobs, updates, kind)
    bino = priority_workload(BinomialHeap, jobs, updates, kind)

    if updates >= 1 and kind == "boost":
        # Property: jobs often jump to the front -> long decrease-key paths -> Fibonacci Heap.
        chosen, other, names = fib, bino, ("Fibonacci Heap", "Binomial Heap")
        complexity = "insert / decrease-key O(1) amortized, extract-min O(log n) amortized"
        reason = ("Jobs are often boosted to the front. In a Binomial Heap each boost bubbles up the "
                  "whole tree (O(log n)), while a Fibonacci Heap just cuts the node out (O(1) amortized).")
    else:
        # Property: priorities are static or only nudged -> Binomial Heap.
        chosen, other, names = bino, fib, ("Binomial Heap", "Fibonacci Heap")
        complexity = "every operation O(log n) worst case"
        reason = ("Priorities are static or change only slightly, so decrease-key stops after about one "
                  "comparison. Binomial gives worst-case O(log n) with no amortized pauses, and "
                  "Fibonacci's extra bookkeeping is not repaid.")
    return {
        "module": "Dynamic job priority",
        "property": f"{jobs} jobs, {updates} priority update(s) per dispatch (type: {kind})",
        "technique": names[0],
        "complexity": complexity,
        "rejected": names[1],
        "reason": reason,
        "result": f"{names[0]}: {chosen['ops']:,} ops, {chosen['time_ms']:.0f} ms vs "
                  f"{names[1]}: {other['ops']:,} ops, {other['time_ms']:.0f} ms",
        "detail": [],
        "measure": {"ops": chosen["ops"], "alt_ops": other["ops"],
                    "time_ms": chosen["time_ms"], "alt_time_ms": other["time_ms"]},
    }


# ---------------------------------------------------------------- Module 5
def build_telemetry_index(scenario):
    """Thermal history is always indexed with a B-Tree (no decision rule needed)."""
    t = scenario["telemetry"]
    bt = telemetry_workload(BTree, t["records"], t["queries"])
    return {
        "module": "Telemetry index",
        "property": f"{t['records']:,} time-ordered readings, append-only, queried by time range",
        "technique": "B-Tree (t=3)",
        "complexity": "O(t log_t n) search/insert, O(t log_t n + k) range query",
        "rejected": "Hash table (no ordered range queries)",
        "reason": "Timestamps are ordered keys and we ask for time ranges, which a hash table cannot answer. "
                  "Wide, shallow nodes suit an append-only log stored in disk blocks, and no deletion is needed.",
        "result": f"height {bt['height']}; {bt['avg_nodes_visited']:.1f} nodes and {bt['avg_comparisons']:.1f} "
                  f"comparisons per search; {bt['splits']:,} splits; last 10 minutes = {bt['range_hits']} readings",
        "detail": [],
        "measure": bt,
    }


def run_scenario(scenario):
    """Run every module of the framework on one scenario."""
    return {
        "name": scenario["name"],
        "budget": scenario["thermal_budget"],
        "jobs": [vars(j) for j in scenario["jobs"]],
        "decisions": [
            decide_job_admission(scenario),
            decide_computation_order(scenario),
            decide_priority_queue(scenario),
            build_telemetry_index(scenario),
        ],
    }


def format_report(report):
    """Human-readable explanation (the EXPLAIN stage)."""
    lines = ["=" * 78, f"SCENARIO: {report['name']}", "=" * 78]
    for d in report["decisions"]:
        lines += [
            f"\n[{d['module']}]",
            f"  Observed property : {d['property']}",
            f"  Chosen technique  : {d['technique']}",
            f"  Complexity        : {d['complexity']}",
            f"  Rejected          : {d['rejected']}",
            f"  Why               : {d['reason']}",
            f"  Result            : {d['result']}",
        ]
        if d["detail"]:
            lines.append("  Admitted          : " + ", ".join(f"{n} ({f:.0%})" for n, f in d["detail"]))
    return "\n".join(lines)
