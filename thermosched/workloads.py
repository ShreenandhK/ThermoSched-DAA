"""Workload simulators shared by the framework and the experiments.

They replay the SAME random sequence of operations on two competing data structures,
so the comparison is fair.
"""

import random
from time import perf_counter


def priority_workload(heap_class, jobs, updates_per_dispatch, kind="aging", seed=7):
    """Simulate a CPU run queue.

    1. `jobs` jobs are inserted with a priority key (smaller = more urgent).
    2. Before every dispatch, `updates_per_dispatch` waiting jobs become more urgent (decrease-key):
         kind="aging" -> small nudge (the job waited a little longer)
         kind="boost" -> big jump to near the front (thermal alarm / deadline reached)
    3. Dispatch = extract-min. Repeat until the queue is empty.
    """
    rng = random.Random(seed)
    heap = heap_class()
    key = {}
    start = perf_counter()

    for j in range(jobs):
        key[j] = rng.randint(10_000, 1_000_000)
        heap.insert(key[j], j)

    waiting = list(range(jobs))      # jobs still in the queue
    position = {j: j for j in waiting}
    decreases = 0
    order = []                       # dispatch order (used by tests)

    while waiting:
        for _ in range(updates_per_dispatch):
            j = waiting[rng.randrange(len(waiting))]
            if kind == "boost":
                key[j] = rng.randint(0, key[j] // 10)
            else:
                key[j] -= rng.randint(1, 5_000)
            heap.decrease_key(j, key[j])
            decreases += 1
        k, j = heap.extract_min()
        order.append(k)
        # O(1) removal from `waiting`: move the last element into j's slot
        i = position.pop(j)
        last = waiting.pop()
        if last != j:
            waiting[i] = last
            position[last] = i

    return {
        "ops": heap.ops,
        "time_ms": (perf_counter() - start) * 1000,
        "inserts": jobs,
        "decrease_keys": decreases,
        "extract_mins": jobs,
        "dispatch_keys": order,
    }


def telemetry_workload(tree_class, records, queries, seed=11):
    """Build a thermal-telemetry index (a B-Tree) and query it.

    Records arrive in timestamp order (a sensor log), which is the worst case for an
    unbalanced BST - a balanced tree is needed. Each record: timestamp -> temperature (deg C).
    """
    rng = random.Random(seed)
    tree = tree_class()
    start = perf_counter()
    for i in range(records):
        tree.insert(i * 5, round(rng.uniform(40.0, 95.0), 1))    # one reading every 5 s
    insert_ms = (perf_counter() - start) * 1000

    comparisons_before = tree.comparisons
    visited = 0
    start = perf_counter()
    for _ in range(queries):
        _, v = tree.search(rng.randrange(records) * 5)
        visited += v
    search_ms = (perf_counter() - start) * 1000

    last_10_min = tree.range_query((records - 120) * 5, records * 5)

    return {
        "height": tree.height(),
        "insert_ms": insert_ms,
        "search_ms": search_ms,
        "avg_nodes_visited": visited / max(queries, 1),
        "avg_comparisons": (tree.comparisons - comparisons_before) / max(queries, 1),
        "range_hits": len(last_10_min),
        "splits": tree.splits,
    }
