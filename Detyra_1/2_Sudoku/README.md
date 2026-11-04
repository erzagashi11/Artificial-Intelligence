# Sudoku Solver: Breadth-First Search with Backtracking

Implementation: [`sudoku.py`](sudoku.py) (Python 3.8+, standard library only)

---

## 1. Problem Statement

A Sudoku is a 9 × 9 grid divided into nine 3 × 3 boxes. Some cells are given at the start. The remaining cells must be filled with the digits 1–9 so that each digit appears **exactly once** in every row, every column and every 3 × 3 box.

The assignment asks for a solver based on **BFS with backtracking** and for puzzles at three difficulty levels. The program solves one puzzle per level:

| Level | Given digits | Empty cells | Source |
|---|---|---|---|
| **Easy** | 36 | 45 | Built for this assignment by removing 45 cells from a completed grid |
| **Medium** | 27 | 54 | Medium-level puzzle |
| **Hard** | 21 | 60 | Arto Inkala's "world's hardest Sudoku" (2012) |

Each puzzle has been checked to have **exactly one solution**. The levels are distinguished by the amount of work BFS needs: about 10², 10⁴ and 10⁶ nodes respectively (see [Results](#8-results)).

---

## 2. Assignment Requirements

| Requirement | Section |
|---|---|
| Model the problem | [3. Problem Model](#3-problem-model) |
| Describe the representation (variables, domain, constraints) | [4. Representation](#4-representation) |
| Formulate the objective function | [5. Objective Function](#5-objective-function) |
| Calculate the landscape | [6. Landscape](#6-landscape) |
| Implement the algorithm: BFS with backtracking, three levels | [7. Algorithm](#7-algorithm-bfs-with-backtracking) |

---

## 3. Problem Model

Sudoku is modelled as a **Constraint Satisfaction Problem (CSP)** and solved as a search problem.

| Element | Definition |
|---|---|
| **State** | A partially filled grid |
| **Initial state** | The given puzzle, with its empty cells |
| **Action** | Place a digit 1–9 in the next empty cell |
| **Goal test** | No empty cell is left and no constraint is violated |
| **Path cost** | Each action costs 1. Every solution lies at the same depth k, the number of empty cells |

A solved Sudoku is a 9 × 9 Latin square (see problem 3) with the additional box constraint.

---

## 4. Representation

### Variables

```
x[r][c]     r = 0 … 8 (row),  c = 0 … 8 (column)
```

There are 81 variables, one per cell. In the code the grid is a list of 81 numbers, `grid[r * 9 + c]`, where `0` marks an empty cell.

### Domain

```
D(x[r][c]) = {1, 2, …, 9}        if the cell is empty
D(x[r][c]) = {given digit}       if the cell is given
```

### Constraints

| | Constraint |
|---|---|
| C1 | Each **row** contains the digits 1–9 exactly once |
| C2 | Each **column** contains the digits 1–9 exactly once |
| C3 | Each **3 × 3 box** contains the digits 1–9 exactly once |
| C4 | The given digits are never changed |

Together, C1–C3 form **27 units** (9 rows, 9 columns, 9 boxes), each of which must contain all digits 1–9.

### Main Functions in the Code

| Function | Purpose |
|---|---|
| `parse(text)` | Converts a puzzle string such as `"53..7...."` into a list of 81 numbers |
| `candidates(grid, i)` | Returns the digits that can be placed in cell `i` without violating C1–C3 |
| `next_cell(grid, mrv)` | Chooses the empty cell to fill next |
| `bfs(start, mrv)` | BFS with backtracking |
| `objective_function(grid)` | Counts constraint violations |
| `verify(grid, start)` | Checks that a solution satisfies all constraints |
| `count_solutions(start)` | Confirms that a puzzle has exactly one solution |

---

## 5. Objective Function

The objective function counts the **repeated digits** across the 27 units:

```
f(S) =      Σ        ( 9 − number of distinct digits in unit u )
       u ∈ 27 units
```

- A row that contains all digits 1–9 contributes 9 − 9 = 0.
- A row that contains the digit 5 twice has only 8 distinct digits and contributes 1.
- **f(S) = 0** means the Sudoku is solved correctly.
- Goal: find a complete grid S with **f(S) = 0**.

In the code this is `objective_function(grid)`. Every solution is verified with it and the program prints `f(S) = 0`.

---

## 6. Landscape

All values below are printed by `python3 sudoku.py --landscape`.

### Full Grid

- 81 cells with 9 values each: **9⁸¹ ≈ 1.97 × 10⁷⁷** possible grids.
- Of these, only **6.67 × 10²¹** are valid completed Sudoku grids (Felgenhauer and Jarvis, 2005).

### Search Space per Level

With k empty cells and 9 values per cell, the naive space is 9^k. If each empty cell may only take the digits that do not clash with the given digits, the space shrinks considerably:

| Level | Givens | Empty (k) | Naive 9^k | With initial candidates | Solutions |
|---|---|---|---|---|---|
| Easy | 36 | 45 | 8.73 × 10⁴² | 5.14 × 10¹⁶ | 1 |
| Medium | 27 | 54 | 3.38 × 10⁵¹ | 3.02 × 10²⁷ | 1 |
| Hard | 21 | 60 | 1.80 × 10⁵⁷ | 9.59 × 10³⁶ | 1 |

### Shape of the Search Tree

- **Depth:** k, the number of empty cells. Each level of the tree fills one cell.
- **Branching:** the number of valid digits for the next cell, between 0 and 9.
- **Solutions:** only at depth k, the deepest level of the tree, and exactly one per puzzle.
- Because only valid digits are expanded, the tree actually explored is many orders of magnitude smaller than the theoretical space. For the Hard puzzle it has about 2 million nodes instead of 10³⁶.

---

## 7. Algorithm: BFS with Backtracking

### Approach

**Breadth-First Search** explores the tree **level by level** using a **FIFO queue**: the grid that entered the queue first is expanded first. All grids with one filled cell are therefore processed before any grid with two, and so on.

**Backtracking** happens in two places:

1. A digit that violates a constraint is never placed, so that child is never created or added to the queue (pruning).
2. If the next empty cell has no valid digit, the grid has no children. The branch is a dead end and is abandoned; BFS continues with the next grid in the queue.

### Pseudocode

```
BFS(start):
    queue ← [start]
    while queue is not empty:
        grid ← queue.pop_front()                     # FIFO
        i ← next empty cell of grid
        if there is no empty cell: return grid       # solution
        for each v in candidates(grid, i):           # valid digits only
            child ← copy of grid
            child[i] ← v
            queue.push_back(child)
        # if candidates(grid, i) is empty, the branch ends here (backtrack)
    return "no solution"
```

### Example

If the first empty cell can take {1, 2, 4}, BFS adds three grids to the queue:

```
queue: [ grid(x=1), grid(x=2), grid(x=4) ]
```

It then takes `grid(x=1)`, finds the candidates of the second empty cell, for example {3, 7}, and appends them at the back:

```
queue: [ grid(x=2), grid(x=4), grid(x=1, y=3), grid(x=1, y=7) ]
```

This continues level by level until a grid with no empty cell is reached.

### Optional Variable Ordering (`--mrv`)

By default BFS always fills the **first empty cell**, row by row, which is a fixed and uninformed order. With `--mrv` (*Minimum Remaining Values*) it fills the cell with the **fewest candidates** first. The algorithm is still BFS; only the choice of cell at each level changes, which makes the tree much narrower. This option is not required by the assignment and is included for comparison.

---

## 8. Results

| Level | BFS, first empty cell | | | BFS with `--mrv` | | |
|---|---|---|---|---|---|---|
| | **Nodes** | **Max queue** | **Time** | **Nodes** | **Max queue** | **Time** |
| Easy | 87 | 6 | < 0.01 s | 46 | 1 | 0.01 s |
| Medium | 23,502 | 6,618 | 0.25 s | 104 | 4 | 0.02 s |
| Hard | 2,068,781 | 356,812 | 24.6 s | 18,936 | 888 | 3.9 s |

All three puzzles are solved correctly, with **f(S) = 0** and a successful verification.

**Interpretation:**
- The work grows by about two orders of magnitude per level: under 100 nodes for Easy, about 23 thousand for Medium and about 2 million for Hard.
- **Max queue** is the number of grids BFS keeps in memory at the same time. For the Hard puzzle it exceeds 350,000 grids. This is the main weakness of BFS: it must hold an entire level of the tree in memory, whereas DFS (as in the Social Golfers problem) only keeps the current path.
- With `--mrv` on the Easy puzzle, the queue never exceeds one grid: every chosen cell has exactly one candidate, so the puzzle is solved without any guessing.

Solution of the Hard puzzle:

```
8 1 2 | 7 5 3 | 6 4 9
9 4 3 | 6 8 2 | 1 7 5
6 7 5 | 4 9 1 | 2 8 3
------+-------+------
1 5 4 | 2 3 7 | 8 9 6
3 6 9 | 8 4 5 | 7 2 1
2 8 7 | 1 6 9 | 5 3 4
------+-------+------
5 2 1 | 9 7 4 | 3 6 8
4 3 8 | 5 2 6 | 9 1 7
7 9 6 | 3 1 8 | 4 5 2
```

---

## 9. How to Run

From this folder:

```bash
python3 sudoku.py                    # landscape + all three levels
python3 sudoku.py --level easy       # one level only (easy, medium or hard)
python3 sudoku.py --landscape        # landscape only
python3 sudoku.py --mrv              # all levels, filling the cell with the fewest candidates first
python3 sudoku.py --level hard --mrv # options can be combined
```

| Option | Description | Default |
|---|---|---|
| `--level` | solve only the given level | all levels |
| `--landscape` | print only the landscape | off |
| `--mrv` | fill the cell with the fewest candidates first | off |
