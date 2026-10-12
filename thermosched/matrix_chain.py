"""Module 3: computation reduction with Matrix Chain Multiplication.

A job multiplies matrices A1 x A2 x ... x An. The result is the same for every bracketing,
but the number of scalar multiplications (our proxy for CPU work and heat) is not.
Matrix Ai has shape dims[i-1] x dims[i].
"""


def matrix_chain_order(dims):
    """Find the bracketing with the fewest scalar multiplications.

    m[i][j] = cheapest cost to multiply Ai..Aj
    m[i][j] = min over k of  m[i][k] + m[k+1][j] + dims[i-1] * dims[k] * dims[j]

    Time  : O(n^3)   (n = number of matrices)
    Space : O(n^2)   (tables m and s)
    """
    n = len(dims) - 1
    m = [[0] * (n + 1) for _ in range(n + 1)]
    s = [[0] * (n + 1) for _ in range(n + 1)]   # s[i][j] = best split point k
    steps = 0                                   # inner-loop iterations (DP work)

    for length in range(2, n + 1):              # chain length being solved
        for i in range(1, n - length + 2):
            j = i + length - 1
            m[i][j] = float("inf")
            for k in range(i, j):
                steps += 1
                cost = m[i][k] + m[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k

    return {
        "optimal_cost": m[1][n] if n >= 1 else 0,
        "order": parenthesize(s, 1, n) if n >= 1 else "",
        "naive_cost": left_to_right_cost(dims),
        "dp_steps": steps,
    }


def parenthesize(s, i, j):
    """Rebuild the optimal bracketing from the split table, e.g. ((A1A2)(A3A4))."""
    if i == j:
        return f"A{i}"
    k = s[i][j]
    return "(" + parenthesize(s, i, k) + parenthesize(s, k + 1, j) + ")"


def left_to_right_cost(dims):
    """Cost of the default order ((A1A2)A3)...An - what a program does without optimisation."""
    cost = 0
    for k in range(2, len(dims)):
        cost += dims[0] * dims[k - 1] * dims[k]
    return cost
