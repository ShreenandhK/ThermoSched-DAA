"""Module 1 + 2: job admission under a thermal budget.

0/1 Knapsack (Dynamic Programming)  -> jobs are indivisible (run fully or not at all)
Fractional Knapsack (Greedy)        -> CPU time is divisible (a job may get part of the budget)
"""


def knapsack_01(jobs, budget):
    """Choose the subset of whole jobs with maximum total benefit whose thermal cost fits the budget.

    dp[i][w] = best benefit using only the first i jobs with a budget of w.
        dp[i][w] = max(dp[i-1][w],                                    # skip job i
                       dp[i-1][w - cost_i] + benefit_i)               # take job i (if it fits)

    Time  : O(n * W)   (n = number of jobs, W = budget)  -> pseudo-polynomial in W
    Space : O(n * W)   (full table is kept so the chosen jobs can be traced back)
    """
    n = len(jobs)
    dp = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        job = jobs[i - 1]
        for w in range(budget + 1):
            dp[i][w] = dp[i - 1][w]                                   # option 1: skip the job
            if job.thermal_cost <= w:
                take = dp[i - 1][w - job.thermal_cost] + job.benefit  # option 2: run the job
                if take > dp[i][w]:
                    dp[i][w] = take

    # Trace back: if the value changed when job i was allowed, job i was taken.
    chosen = []
    w = budget
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(jobs[i - 1])
            w -= jobs[i - 1].thermal_cost
    chosen.reverse()

    return {
        "benefit": dp[n][budget],
        "chosen": chosen,
        "used": sum(j.thermal_cost for j in chosen),
        "cells": (n + 1) * (budget + 1),   # DP table size = work done
    }


def fractional_knapsack(jobs, budget):
    """Give the budget to jobs in decreasing benefit/cost order; the last job may get a fraction.

    Greedy choice property: when items are divisible, the highest benefit-per-unit item is always
    part of some optimal answer, so the greedy order is optimal.

    Time  : O(n log n)  (sorting dominates; the scan is O(n))
    Space : O(n)
    """
    order = sorted(jobs, key=lambda j: j.ratio, reverse=True)
    remaining = budget
    total = 0.0
    shares = []                                    # (job, fraction of the job admitted)

    for job in order:
        if remaining <= 0:
            break
        fraction = min(1.0, remaining / job.thermal_cost)
        total += fraction * job.benefit
        remaining -= fraction * job.thermal_cost
        shares.append((job, fraction))

    return {"benefit": total, "shares": shares, "used": budget - remaining}


def greedy_whole_jobs(jobs, budget):
    """Baseline: the fractional greedy rule applied to whole jobs.

    Shown only to prove that greedy is NOT optimal for indivisible jobs.
    Time: O(n log n), Space: O(n)
    """
    chosen = []
    used = 0
    for job in sorted(jobs, key=lambda j: j.ratio, reverse=True):
        if used + job.thermal_cost <= budget:
            chosen.append(job)
            used += job.thermal_cost
    return {"benefit": sum(j.benefit for j in chosen), "chosen": chosen, "used": used}
