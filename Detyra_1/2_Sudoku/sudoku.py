"""
Sudoku Solver: Breadth-First Search with Backtracking

A 9x9 grid must be filled so that every row, every column and every 3x3 box
contains the digits 1..9 exactly once. The program solves three puzzles:
Easy, Medium and Hard.

Usage:
    python sudoku.py                  # landscape + all three levels
    python sudoku.py --level easy     # one level only (easy / medium / hard)
    python sudoku.py --landscape      # landscape only
    python sudoku.py --mrv            # BFS that picks the cell with the fewest options
"""

import argparse
import math
import time
from collections import deque


# ---------------------------------------------------------------------
#  The three levels ('.' = empty cell, read row by row)
# ---------------------------------------------------------------------
PUZZLES = {
    "easy": (
        ".2.8.3547"
        "8.7.51..3"
        "..3...1.6"
        ".156.49.."
        "9.8.1..5."
        "....7.3.."
        "5.....73."
        "7..9..82."
        "2.17....5"
    ),
    "medium": (
        "..9748..."
        "7........"
        ".2.1.9..."
        "..7...24."
        ".64.1.59."
        ".98...3.."
        "...8.3.2."
        "........6"
        "...2759.."
    ),
    "hard": (
        "8........"
        "..36....."
        ".7..9.2.."
        ".5...7..."
        "....457.."
        "...1...3."
        "..1....68"
        "..85...1."
        ".9....4.."
    ),
}


# ---------------------------------------------------------------------
#  Representation
#
#  grid = list of 81 numbers, row by row.
#  grid[r * 9 + c] = the cell in row r, column c.  0 = empty.
# ---------------------------------------------------------------------
def parse(text):
    """Turns a string such as '53..7....' into a list of 81 numbers (0 = empty)."""
    return [0 if ch == "." else int(ch) for ch in text]


def candidates(grid, i):
    """Digits 1..9 that can be placed in cell i without breaking any constraint."""
    r, c = divmod(i, 9)
    used = set()
    for k in range(9):
        used.add(grid[r * 9 + k])               # row
        used.add(grid[k * 9 + c])               # column
    r0, c0 = 3 * (r // 3), 3 * (c // 3)         # top-left corner of the 3x3 box
    for a in range(3):
        for b in range(3):
            used.add(grid[(r0 + a) * 9 + (c0 + b)])
    return [v for v in range(1, 10) if v not in used]


def next_cell(grid, mrv=False):
    """The empty cell to fill next, or None if the grid is full."""
    empty = [i for i in range(81) if grid[i] == 0]
    if not empty:
        return None
    if mrv:
        return min(empty, key=lambda i: len(candidates(grid, i)))
    return empty[0]


# ---------------------------------------------------------------------
#  BFS with backtracking
#
#  The queue holds partially filled grids.
#  - Take the oldest grid from the queue (FIFO -> level by level).
#  - Find the next empty cell and create one child for every VALID digit.
#  - Digits that break a constraint are never put in the queue, and a grid
#    with no valid digit gets no children: that branch is abandoned
#    (backtracking).
# ---------------------------------------------------------------------
def bfs(start, mrv=False):
    queue = deque([start])
    nodes = 0                   # grids taken from the queue
    max_queue = 1               # largest queue size (memory)

    while queue:
        grid = queue.popleft()
        nodes += 1

        i = next_cell(grid, mrv)
        if i is None:
            return grid, nodes, max_queue            # no empty cell left: solution

        for v in candidates(grid, i):                # valid digits only
            child = grid[:]
            child[i] = v
            queue.append(child)

        # If candidates() was empty, this grid has no children:
        # the branch dies here (backtrack) and BFS continues with the next grid.

        max_queue = max(max_queue, len(queue))

    return None, nodes, max_queue                    # no solution


# ---------------------------------------------------------------------
#  Objective function
#  f(S) = number of repeated digits in rows, columns and 3x3 boxes.
#  For each of the 27 units: 9 - (number of distinct digits).
#  f(S) = 0 means the Sudoku is solved correctly.
# ---------------------------------------------------------------------
def units():
    """The 27 units: 9 rows, 9 columns and 9 boxes, each as 9 cell indices."""
    rows = [[r * 9 + c for c in range(9)] for r in range(9)]
    cols = [[r * 9 + c for r in range(9)] for c in range(9)]
    boxes = [[(r0 + a) * 9 + (c0 + b) for a in range(3) for b in range(3)]
             for r0 in (0, 3, 6) for c0 in (0, 3, 6)]
    return rows + cols + boxes


def objective_function(grid):
    return sum(9 - len({grid[i] for i in unit}) for unit in units())


def verify(grid, start):
    """The grid is full, f(S) = 0, and the given digits were not changed."""
    if 0 in grid:
        return False
    if any(start[i] != 0 and start[i] != grid[i] for i in range(81)):
        return False
    return objective_function(grid) == 0


def count_solutions(start, limit=2):
    """Counts solutions with a small DFS, stopping at `limit`. A proper Sudoku has exactly 1."""
    grid = start[:]
    count = 0

    def search():
        nonlocal count
        i = next_cell(grid)
        if i is None:
            count += 1
            return count >= limit
        for v in candidates(grid, i):
            grid[i] = v
            if search():
                return True
            grid[i] = 0
        return False

    search()
    return count


# ---------------------------------------------------------------------
#  Landscape
# ---------------------------------------------------------------------
def landscape():
    print("=== LANDSCAPE ===\n")
    print("Full grid (no given digits):")
    print(f"  81 cells, each 1..9:        9^81 = {9 ** 81:.3e}")
    print("  Valid completed Sudoku grids:     6.671e+21  (known result)\n")

    print(f"{'Level':8s} {'givens':>7s} {'empty (k)':>10s} {'9^k (naive)':>13s} "
          f"{'with candidates':>16s} {'solutions':>10s}")
    for name, text in PUZZLES.items():
        grid = parse(text)
        empty = [i for i in range(81) if grid[i] == 0]
        k = len(empty)
        reduced = math.prod(len(candidates(grid, i)) for i in empty)
        print(f"{name:8s} {81 - k:7d} {k:10d} {9 ** k:13.3e} {reduced:16.3e} {count_solutions(grid):10d}")
    print("\n  givens          = digits given at the start")
    print("  9^k             = every empty cell can take 9 values")
    print("  with candidates = every empty cell takes only the digits that do not clash with the givens")
    print("  solutions       = number of solutions (a proper Sudoku has exactly 1)")
    print("  The depth of the search tree equals k, the number of empty cells.\n")


# ---------------------------------------------------------------------
#  Output and main program
# ---------------------------------------------------------------------
def print_grid(grid):
    for r in range(9):
        if r in (3, 6):
            print("------+-------+------")
        cells = [str(v) if v else "." for v in grid[r * 9:(r + 1) * 9]]
        print(" ".join(cells[0:3]) + " | " + " ".join(cells[3:6]) + " | " + " ".join(cells[6:9]))


def solve_level(name, mrv=False):
    start = parse(PUZZLES[name])
    print(f"=== {name.upper()}  ({start.count(0)} empty cells) ===\n")
    print_grid(start)

    t = time.time()
    solution, nodes, max_queue = bfs(start, mrv)
    elapsed = time.time() - t

    if solution is None:
        print(f"\nNO SOLUTION  ({nodes} nodes)")
        return
    print(f"\nSolution ({nodes} nodes, max queue = {max_queue}, {elapsed:.2f} s):\n")
    print_grid(solution)
    print(f"\nObjective function f(S) = {objective_function(solution)}  (0 = no repeated digit)")
    print(f"Verification: {'OK' if verify(solution, start) else 'FAILED'}\n")


def main():
    parser = argparse.ArgumentParser(description="Sudoku: BFS with backtracking")
    parser.add_argument("--level", choices=list(PUZZLES), help="solve one level only")
    parser.add_argument("--landscape", action="store_true", help="print the landscape only")
    parser.add_argument("--mrv", action="store_true", help="fill the cell with the fewest candidates first")
    args = parser.parse_args()

    if args.landscape:
        landscape()
    elif args.level:
        solve_level(args.level, args.mrv)
    else:
        landscape()
        for name in PUZZLES:
            solve_level(name, args.mrv)


if __name__ == "__main__":
    main()
