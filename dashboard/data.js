window.THERMO_DATA = {
 "scenarios": [
  {
   "name": "Night batch - time-sliced jobs, static priorities",
   "budget": 50,
   "jobs": [
    {
     "name": "J1 Matrix render",
     "benefit": 60,
     "thermal_cost": 10
    },
    {
     "name": "J2 Log analytics",
     "benefit": 100,
     "thermal_cost": 20
    },
    {
     "name": "J3 Video encode",
     "benefit": 120,
     "thermal_cost": 30
    },
    {
     "name": "J4 ML training",
     "benefit": 90,
     "thermal_cost": 25
    },
    {
     "name": "J5 Backup compress",
     "benefit": 30,
     "thermal_cost": 15
    }
   ],
   "decisions": [
    {
     "module": "Job admission",
     "property": "CPU time is divisible (jobs can receive a fraction of the budget)",
     "technique": "Fractional Knapsack (Greedy)",
     "complexity": "O(n log n) time, O(n) space",
     "rejected": "0/1 Knapsack DP",
     "reason": "With divisible items the highest benefit-per-heat job is always in an optimal answer (greedy-choice property), so sorting by ratio is optimal and faster.",
     "result": "benefit 240.0, budget used 50.0/50",
     "detail": [
      [
       "J1 Matrix render",
       1.0
      ],
      [
       "J2 Log analytics",
       1.0
      ],
      [
       "J3 Video encode",
       0.667
      ]
     ],
     "measure": {
      "time_ms": 0.010499963536858559,
      "benefit": 240.0,
      "alt_benefit": 220,
      "alt_time_ms": 0.03800005652010441
     }
    },
    {
     "module": "Computation reduction",
     "property": "chain of 2 matrices",
     "technique": "Direct multiplication (no optimisation needed)",
     "complexity": "O(1) decision",
     "rejected": "Matrix Chain Multiplication DP",
     "reason": "With fewer than 3 matrices there is only one bracketing, so DP adds cost and no benefit.",
     "result": "single possible order",
     "detail": [],
     "measure": {}
    },
    {
     "module": "Dynamic job priority",
     "property": "5000 jobs, 0 priority update(s) per dispatch (type: none)",
     "technique": "Binomial Heap",
     "complexity": "every operation O(log n) worst case",
     "rejected": "Fibonacci Heap",
     "reason": "Priorities are static or change only slightly, so decrease-key stops after about one comparison. Binomial gives worst-case O(log n) with no amortized pauses, and Fibonacci's extra bookkeeping is not repaid.",
     "result": "Binomial Heap: 171,800 ops, 45 ms vs Fibonacci Heap: 235,312 ops, 42 ms",
     "detail": [],
     "measure": {
      "ops": 171800,
      "alt_ops": 235312,
      "time_ms": 44.63489982299507,
      "alt_time_ms": 41.998100001364946
     }
    },
    {
     "module": "Telemetry index",
     "property": "20,000 time-ordered readings, append-only, queried by time range",
     "technique": "B-Tree (t=3)",
     "complexity": "O(t log_t n) search/insert, O(t log_t n + k) range query",
     "rejected": "Hash table (no ordered range queries)",
     "reason": "Timestamps are ordered keys and we ask for time ranges, which a hash table cannot answer. Wide, shallow nodes suit an append-only log stored in disk blocks, and no deletion is needed.",
     "result": "height 9; 8.5 nodes and 16.6 comparisons per search; 9,987 splits; last 10 minutes = 120 readings",
     "detail": [],
     "measure": {
      "height": 9,
      "insert_ms": 44.72589981742203,
      "search_ms": 5.333899985998869,
      "avg_nodes_visited": 8.5245,
      "avg_comparisons": 16.6095,
      "range_hits": 120,
      "splits": 9987
     }
    }
   ]
  },
  {
   "name": "Peak hours - interactive server under heavy load",
   "budget": 50,
   "jobs": [
    {
     "name": "J1 Matrix render",
     "benefit": 60,
     "thermal_cost": 10
    },
    {
     "name": "J2 Log analytics",
     "benefit": 100,
     "thermal_cost": 20
    },
    {
     "name": "J3 Video encode",
     "benefit": 120,
     "thermal_cost": 30
    },
    {
     "name": "J4 ML training",
     "benefit": 90,
     "thermal_cost": 25
    },
    {
     "name": "J5 Backup compress",
     "benefit": 30,
     "thermal_cost": 15
    }
   ],
   "decisions": [
    {
     "module": "Job admission",
     "property": "jobs are indivisible (a job runs completely or not at all)",
     "technique": "0/1 Knapsack (Dynamic Programming)",
     "complexity": "O(n*W) time, O(n*W) space (pseudo-polynomial in W)",
     "rejected": "Greedy by benefit/heat ratio",
     "reason": "Greedy is not safe when jobs cannot be split; the DP compares the best answer with and without every job, so it is always optimal.",
     "result": "benefit 220, budget used 50/50",
     "detail": [
      [
       "J2 Log analytics",
       1
      ],
      [
       "J3 Video encode",
       1
      ]
     ],
     "measure": {
      "time_ms": 0.017399899661540985,
      "benefit": 220,
      "dp_cells": 66,
      "gcd_scale": 5,
      "alt_benefit": 190,
      "alt_time_ms": 0.008100178092718124
     }
    },
    {
     "module": "Computation reduction",
     "property": "chain of 4 matrices, dims [10, 30, 5, 60, 10]",
     "technique": "Matrix Chain Multiplication (Dynamic Programming)",
     "complexity": "O(n^3) time, O(n^2) space",
     "rejected": "Left-to-right multiplication",
     "reason": "Bracketing does not change the result but changes the scalar multiplications (our CPU-load proxy); DP finds the cheapest bracketing.",
     "result": "((A1A2)(A3A4)): 5,000 mults vs 10,500 left-to-right (52.4% less work)",
     "detail": [],
     "measure": {
      "time_ms": 0.01940014772117138,
      "optimal": 5000,
      "naive": 10500,
      "saved_pct": 52.38095238095239
     }
    },
    {
     "module": "Dynamic job priority",
     "property": "5000 jobs, 1 priority update(s) per dispatch (type: boost)",
     "technique": "Fibonacci Heap",
     "complexity": "insert / decrease-key O(1) amortized, extract-min O(log n) amortized",
     "rejected": "Binomial Heap",
     "reason": "Jobs are often boosted to the front. In a Binomial Heap each boost bubbles up the whole tree (O(log n)), while a Fibonacci Heap just cuts the node out (O(1) amortized).",
     "result": "Fibonacci Heap: 117,028 ops, 30 ms vs Binomial Heap: 217,285 ops, 52 ms",
     "detail": [],
     "measure": {
      "ops": 117028,
      "alt_ops": 217285,
      "time_ms": 29.67349998652935,
      "alt_time_ms": 52.259699907153845
     }
    },
    {
     "module": "Telemetry index",
     "property": "20,000 time-ordered readings, append-only, queried by time range",
     "technique": "B-Tree (t=3)",
     "complexity": "O(t log_t n) search/insert, O(t log_t n + k) range query",
     "rejected": "Hash table (no ordered range queries)",
     "reason": "Timestamps are ordered keys and we ask for time ranges, which a hash table cannot answer. Wide, shallow nodes suit an append-only log stored in disk blocks, and no deletion is needed.",
     "result": "height 9; 8.5 nodes and 16.6 comparisons per search; 9,987 splits; last 10 minutes = 120 readings",
     "detail": [],
     "measure": {
      "height": 9,
      "insert_ms": 40.184800047427416,
      "search_ms": 4.991699941456318,
      "avg_nodes_visited": 8.5245,
      "avg_comparisons": 16.6095,
      "range_hits": 120,
      "splits": 9987
     }
    }
   ]
  }
 ],
 "experiments": {
  "knapsack_scaling": [
   {
    "n": 25,
    "W": 100,
    "dp_cells": 2626,
    "dp_ms": 0.225,
    "dp_peak_kib": 38.2,
    "frac_ms": 0.005,
    "dp_benefit": 718,
    "frac_benefit": 735.7
   },
   {
    "n": 25,
    "W": 1000,
    "dp_cells": 26026,
    "dp_ms": 2.516,
    "dp_peak_kib": 423.3,
    "frac_ms": 0.005,
    "dp_benefit": 803,
    "frac_benefit": 808.9
   },
   {
    "n": 25,
    "W": 5000,
    "dp_cells": 130026,
    "dp_ms": 13.114,
    "dp_peak_kib": 2051.1,
    "frac_ms": 0.005,
    "dp_benefit": 775,
    "frac_benefit": 793.4
   },
   {
    "n": 50,
    "W": 100,
    "dp_cells": 5151,
    "dp_ms": 0.516,
    "dp_peak_kib": 76.2,
    "frac_ms": 0.009,
    "dp_benefit": 1096,
    "frac_benefit": 1106.0
   },
   {
    "n": 50,
    "W": 1000,
    "dp_cells": 51051,
    "dp_ms": 5.72,
    "dp_peak_kib": 794.9,
    "frac_ms": 0.01,
    "dp_benefit": 1072,
    "frac_benefit": 1092.6
   },
   {
    "n": 50,
    "W": 5000,
    "dp_cells": 255051,
    "dp_ms": 29.989,
    "dp_peak_kib": 3584.2,
    "frac_ms": 0.01,
    "dp_benefit": 915,
    "frac_benefit": 927.0
   },
   {
    "n": 100,
    "W": 100,
    "dp_cells": 10201,
    "dp_ms": 0.948,
    "dp_peak_kib": 139.8,
    "frac_ms": 0.014,
    "dp_benefit": 1349,
    "frac_benefit": 1361.6
   },
   {
    "n": 100,
    "W": 1000,
    "dp_cells": 101101,
    "dp_ms": 9.83,
    "dp_peak_kib": 1519.6,
    "frac_ms": 0.014,
    "dp_benefit": 1629,
    "frac_benefit": 1633.7
   },
   {
    "n": 100,
    "W": 5000,
    "dp_cells": 505101,
    "dp_ms": 53.583,
    "dp_peak_kib": 7775.8,
    "frac_ms": 0.016,
    "dp_benefit": 1652,
    "frac_benefit": 1656.8
   },
   {
    "n": 200,
    "W": 100,
    "dp_cells": 20301,
    "dp_ms": 1.795,
    "dp_peak_kib": 277.5,
    "frac_ms": 0.027,
    "dp_benefit": 2174,
    "frac_benefit": 2175.5
   },
   {
    "n": 200,
    "W": 1000,
    "dp_cells": 201201,
    "dp_ms": 23.288,
    "dp_peak_kib": 2674.8,
    "frac_ms": 0.045,
    "dp_benefit": 2225,
    "frac_benefit": 2227.2
   },
   {
    "n": 200,
    "W": 5000,
    "dp_cells": 1005201,
    "dp_ms": 107.476,
    "dp_peak_kib": 13448.0,
    "frac_ms": 0.034,
    "dp_benefit": 2335,
    "frac_benefit": 2345.5
   }
  ],
  "knapsack_quality": [
   {
    "n": 5,
    "trials": 300,
    "greedy_wrong_pct": 21.7,
    "avg_gap_when_wrong_pct": 10.08
   },
   {
    "n": 10,
    "trials": 300,
    "greedy_wrong_pct": 36.0,
    "avg_gap_when_wrong_pct": 3.38
   },
   {
    "n": 20,
    "trials": 300,
    "greedy_wrong_pct": 47.7,
    "avg_gap_when_wrong_pct": 1.54
   },
   {
    "n": 40,
    "trials": 300,
    "greedy_wrong_pct": 61.7,
    "avg_gap_when_wrong_pct": 0.57
   }
  ],
  "matrix_chain_scaling": [
   {
    "n": 5,
    "dp_steps": 20,
    "dp_ms": 0.011,
    "naive_cost": 449050,
    "optimal_cost": 332934,
    "saved_pct": 25.9
   },
   {
    "n": 10,
    "dp_steps": 165,
    "dp_ms": 0.047,
    "naive_cost": 1205490,
    "optimal_cost": 150444,
    "saved_pct": 87.5
   },
   {
    "n": 20,
    "dp_steps": 1330,
    "dp_ms": 0.27,
    "naive_cost": 4622496,
    "optimal_cost": 344310,
    "saved_pct": 92.6
   },
   {
    "n": 40,
    "dp_steps": 10660,
    "dp_ms": 1.795,
    "naive_cost": 1156312,
    "optimal_cost": 1151000,
    "saved_pct": 0.5
   },
   {
    "n": 80,
    "dp_steps": 85320,
    "dp_ms": 13.525,
    "naive_cost": 5674975,
    "optimal_cost": 1152795,
    "saved_pct": 79.7
   },
   {
    "n": 160,
    "dp_steps": 682640,
    "dp_ms": 90.344,
    "naive_cost": 16919158,
    "optimal_cost": 2247077,
    "saved_pct": 86.7
   }
  ],
  "heap_comparison": [
   {
    "n": 1000,
    "updates_per_dispatch": 0,
    "update_kind": "none",
    "binomial_ops": 26021,
    "fibonacci_ops": 36252,
    "binomial_ms": 6.4,
    "fibonacci_ms": 9.0
   },
   {
    "n": 1000,
    "updates_per_dispatch": 4,
    "update_kind": "aging",
    "binomial_ops": 30208,
    "fibonacci_ops": 44777,
    "binomial_ms": 10.1,
    "fibonacci_ms": 9.0
   },
   {
    "n": 1000,
    "updates_per_dispatch": 1,
    "update_kind": "boost",
    "binomial_ops": 32931,
    "fibonacci_ops": 21215,
    "binomial_ms": 8.8,
    "fibonacci_ms": 5.2
   },
   {
    "n": 1000,
    "updates_per_dispatch": 4,
    "update_kind": "boost",
    "binomial_ops": 35708,
    "fibonacci_ops": 44042,
    "binomial_ms": 11.6,
    "fibonacci_ms": 10.8
   },
   {
    "n": 5000,
    "updates_per_dispatch": 0,
    "update_kind": "none",
    "binomial_ops": 171800,
    "fibonacci_ops": 235312,
    "binomial_ms": 47.5,
    "fibonacci_ms": 41.8
   },
   {
    "n": 5000,
    "updates_per_dispatch": 4,
    "update_kind": "aging",
    "binomial_ops": 193583,
    "fibonacci_ops": 275516,
    "binomial_ms": 62.1,
    "fibonacci_ms": 57.3
   },
   {
    "n": 5000,
    "updates_per_dispatch": 1,
    "update_kind": "boost",
    "binomial_ops": 217285,
    "fibonacci_ops": 117028,
    "binomial_ms": 61.1,
    "fibonacci_ms": 30.9
   },
   {
    "n": 5000,
    "updates_per_dispatch": 4,
    "update_kind": "boost",
    "binomial_ops": 222300,
    "fibonacci_ops": 244077,
    "binomial_ms": 70.1,
    "fibonacci_ms": 60.6
   },
   {
    "n": 20000,
    "updates_per_dispatch": 0,
    "update_kind": "none",
    "binomial_ops": 825301,
    "fibonacci_ops": 1121172,
    "binomial_ms": 217.0,
    "fibonacci_ms": 187.8
   },
   {
    "n": 20000,
    "updates_per_dispatch": 4,
    "update_kind": "aging",
    "binomial_ops": 914882,
    "fibonacci_ops": 1276598,
    "binomial_ms": 303.4,
    "fibonacci_ms": 281.8
   },
   {
    "n": 20000,
    "updates_per_dispatch": 1,
    "update_kind": "boost",
    "binomial_ops": 1042411,
    "fibonacci_ops": 511932,
    "binomial_ms": 261.0,
    "fibonacci_ms": 140.1
   },
   {
    "n": 20000,
    "updates_per_dispatch": 4,
    "update_kind": "boost",
    "binomial_ops": 1021986,
    "fibonacci_ops": 1054581,
    "binomial_ms": 305.1,
    "fibonacci_ms": 274.8
   }
  ],
  "btree_scaling": [
   {
    "n": 1000,
    "height": 6,
    "height_bound": 6.66,
    "nodes_visited": 5.52,
    "comparisons": 11.22,
    "splits": 491,
    "insert_ms": 1.6
   },
   {
    "n": 10000,
    "height": 8,
    "height_bound": 8.75,
    "nodes_visited": 7.53,
    "comparisons": 15.72,
    "splits": 4988,
    "insert_ms": 21.2
   },
   {
    "n": 50000,
    "height": 10,
    "height_bound": 10.22,
    "nodes_visited": 9.49,
    "comparisons": 18.87,
    "splits": 24984,
    "insert_ms": 123.9
   }
  ]
 }
};
