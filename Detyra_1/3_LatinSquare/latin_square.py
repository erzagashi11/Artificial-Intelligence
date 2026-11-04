"""
Latin Square: Iterative Deepening Depth-First Search (IDDFS) with Backtracking

An n x n grid is filled with the numbers 1..n so that every number appears
exactly once in every row and in every column.

Usage:
    python latin_square.py                 # n = 5: landscape, IDDFS and DFS comparison
    python latin_square.py 6               # another size
    python latin_square.py 5 --landscape   # landscape only
    python latin_square.py 7 --time 120    # change the time limit (seconds)
"""

import argparse
import math
import time


# Number of Latin squares for each n (known values, OEIS A002860)
LATIN_SQUARE_COUNTS = {1: 1, 2: 2, 3: 12, 4: 576, 5: 161280, 6: 812851200,
                       7: 61479419904000, 8: 108776032459082956800}

FOUND, CUTOFF, FAILURE = "found", "cutoff", "failure"


class TimeUp(Exception):
    """Raised when the time limit is exceeded."""


class LatinSquare:
    """
    Representation:
        grid[r][c] = the number in row r, column c (0 = empty)
        cells      = the empty cells, in the order they are filled (row by row)

    Symmetry breaking: the first row and the first column are fixed as 1 2 ... n.
    Every Latin square can be brought into this form by renaming the numbers and
    reordering the rows, so no solution is lost.
    """

    def __init__(self, n, time_limit=60):
        self.n = n
        self.time_limit = time_limit
        self.grid = []
        self.cells = []
        self.nodes = 0
        self.start_time = 0.0

    def reset(self):
        n = self.n
        self.grid = [[0] * n for _ in range(n)]
        for c in range(n):
            self.grid[0][c] = c + 1             # first row: 1 2 ... n
        for r in range(n):
            self.grid[r][0] = r + 1             # first column: 1 2 ... n
        self.cells = [(r, c) for r in range(n) for c in range(n) if self.grid[r][c] == 0]
        self.nodes = 0
        self.start_time = time.time()

    def elapsed(self):
        return time.time() - self.start_time

    def can_place(self, r, c, v):
        """True if v is not yet in row r or column c."""
        grid = self.grid
        for k in range(self.n):
            if grid[r][k] == v or grid[k][c] == v:
                return False
        return True

    # ------------------------------------------------------------------
    #  DLS: depth-limited DFS
    # ------------------------------------------------------------------
    def dls(self, i, limit):
        """
        i     = number of cells filled so far (the depth in the tree)
        limit = how many more levels we may go down

        Returns:
            FOUND    - the square is complete
            CUTOFF   - the depth limit stopped the search; a solution may lie deeper
            FAILURE  - this subtree has no solution at any depth
        """
        self.nodes += 1
        if self.nodes % 10000 == 0 and self.elapsed() > self.time_limit:
            raise TimeUp                             # checked every 10,000 nodes to stay fast

        if i == len(self.cells):
            return FOUND
        if limit == 0:
            return CUTOFF

        r, c = self.cells[i]
        cutoff = False
        for v in range(1, self.n + 1):
            if self.can_place(r, c, v):
                self.grid[r][c] = v                  # step forward
                result = self.dls(i + 1, limit - 1)
                if result == FOUND:
                    return FOUND
                if result == CUTOFF:
                    cutoff = True
                self.grid[r][c] = 0                  # backtrack: undo and try the next value

        return CUTOFF if cutoff else FAILURE

    # ------------------------------------------------------------------
    #  IDDFS: DLS with limit 0, 1, 2, ... until a solution is found
    # ------------------------------------------------------------------
    def iddfs(self, verbose=True):
        """Returns (result, limit) and records the nodes of every iteration."""
        self.reset()
        if verbose:
            print(f"Cells to fill: {len(self.cells)}  (first row and column are fixed)\n")
            print(f"{'limit':>6s} {'nodes in iteration':>19s} {'total nodes':>12s}")

        limit = 0
        while True:
            before = self.nodes
            try:
                result = self.dls(0, limit)
            except TimeUp:
                if verbose:
                    print(f"\nTime limit reached ({self.time_limit:g} s) during iteration {limit}.")
                return "timeout", limit
            if verbose:
                print(f"{limit:6d} {self.nodes - before:19d} {self.nodes:12d}")
            if result == FOUND:
                return FOUND, limit
            if result == FAILURE:                    # nothing was cut off: no solution exists
                return FAILURE, limit
            limit += 1

    # ------------------------------------------------------------------
    #  Plain DFS (no depth limit), for comparison
    # ------------------------------------------------------------------
    def dfs(self):
        self.reset()
        try:
            return self.dls(0, len(self.cells)) == FOUND
        except TimeUp:
            return False


# ---------------------------------------------------------------------
#  Objective function
#  f(S) = number of repeated values in rows and columns.
#  For every row and column: n - (number of distinct values).
#  f(S) = 0 means S is a valid Latin square.
# ---------------------------------------------------------------------
def objective_function(grid):
    n = len(grid)
    f = sum(n - len(set(row)) for row in grid)
    f += sum(n - len({grid[r][c] for r in range(n)}) for c in range(n))
    return f


def verify(grid):
    n = len(grid)
    if any(v < 1 or v > n for row in grid for v in row):
        return False
    return objective_function(grid) == 0


# ---------------------------------------------------------------------
#  Landscape
# ---------------------------------------------------------------------
def landscape(n):
    print(f"=== LANDSCAPE (n = {n}) ===\n")
    print(f"Variables: n^2 = {n * n}   Domain: {{1..{n}}}\n")

    print("Size of the search space:")
    print(f"  a) naive, every cell 1..n:             n^(n^2) = {n}^{n * n} = {n ** (n * n):.3e}")
    print(f"  b) every row a permutation:            (n!)^n  = {math.factorial(n) ** n:.3e}")
    print(f"  c) first row and column fixed:         (n-1)^((n-1)^2) = {(n - 1) ** ((n - 1) ** 2):.3e}")
    if n in LATIN_SQUARE_COUNTS:
        total = LATIN_SQUARE_COUNTS[n]
        reduced = total // (math.factorial(n) * math.factorial(n - 1))
        print(f"\nLatin squares that actually exist:     {total:,}")
        print(f"  in reduced form (first row and column fixed): {reduced:,}")
    print(f"\nDepth of the tree: {(n - 1) ** 2} cells (excluding the first row and column)")
    print(f"Maximum branching: {n - 1} (values that can go into one cell)\n")

    print("Comparison for different n:")
    print(f"  {'n':>2s} {'n^(n^2)':>12s} {'Latin squares':>24s}")
    for m in range(2, 9):
        print(f"  {m:2d} {m ** (m * m):12.3e} {LATIN_SQUARE_COUNTS[m]:24,}")
    print()


# ---------------------------------------------------------------------
#  Main program
# ---------------------------------------------------------------------
def print_grid(grid):
    for row in grid:
        print(" ".join(f"{v:2d}" for v in row))


def main():
    parser = argparse.ArgumentParser(description="Latin Square: IDDFS with backtracking")
    parser.add_argument("n", type=int, nargs="?", default=5, help="size of the square (default 5)")
    parser.add_argument("--landscape", action="store_true", help="print the landscape only")
    parser.add_argument("--time", type=float, default=60, help="time limit in seconds (default 60)")
    args = parser.parse_args()
    n = args.n

    landscape(n)
    if args.landscape:
        return

    square = LatinSquare(n, args.time)

    print(f"=== IDDFS WITH BACKTRACKING (n = {n}) ===\n")
    result, limit = square.iddfs()
    iddfs_nodes, iddfs_time = square.nodes, square.elapsed()
    if result == FOUND:
        print(f"\nFOUND with limit {limit}  ({iddfs_nodes} nodes in total, {iddfs_time:.2f} s)\n")
        print_grid(square.grid)
        print(f"\nObjective function f(S) = {objective_function(square.grid)}  (0 = no repeated value)")
        print(f"Verification: {'OK' if verify(square.grid) else 'FAILED'}")
    elif result == FAILURE:
        print(f"\nNO SOLUTION exists  ({iddfs_nodes} nodes, {iddfs_time:.2f} s)")
    else:
        print(f"NOT FOUND within the time limit  ({iddfs_nodes} nodes, {iddfs_time:.2f} s)")

    print(f"\n=== COMPARISON: PLAIN DFS (no depth limit, n = {n}) ===\n")
    found = square.dfs()
    print(f"DFS:   {'found' if found else 'not found'}, {square.nodes} nodes, {square.elapsed():.2f} s")
    print(f"IDDFS: {'found' if result == FOUND else 'not found'}, {iddfs_nodes} nodes, {iddfs_time:.2f} s")
    if found and result != FOUND:
        print("\nSolution found by DFS:\n")
        print_grid(square.grid)
        print(f"\nObjective function f(S) = {objective_function(square.grid)}")


if __name__ == "__main__":
    main()
