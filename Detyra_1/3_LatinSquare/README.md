# Latin Square: Iterative Deepening DFS with Backtracking

Implementation: [`latin_square.py`](latin_square.py) (Python 3.8+, standard library only)

---

## 1. Problem Statement

A **Latin square** of order n is an n × n grid filled with the numbers 1 … n so that each number appears **exactly once in every row and exactly once in every column**. Given n, the program must output one such square.

Example output of the program for n = 5:

```
1 2 3 4 5
2 1 4 5 3
3 4 5 1 2
4 5 2 3 1
5 3 1 2 4
```

**Note on the example in the assignment.** The example for n = 5 in the assignment shows only four rows:

```
5 1 2 3 4
4 5 1 2 3
3 4 5 1 2
2 3 4 5 1
```

The missing row is `1 2 3 4 5`: with it, the example is the complete 5 × 5 square in which each row is the previous one shifted one position to the right. The row was most likely lost when the assignment was formatted, because a line written directly after the opening ```` ``` ```` of a Markdown code block is read as the block's language label and is not displayed. Any valid Latin square is an acceptable answer; the square above is the one our search finds.

---

## 2. Assignment Requirements

| Requirement | Section |
|---|---|
| Model the problem | [3. Problem Model](#3-problem-model) |
| Describe the representation (variables, domain, constraints) | [4. Representation](#4-representation) |
| Formulate the objective function | [5. Objective Function](#5-objective-function) |
| Calculate the landscape | [6. Landscape](#6-landscape) |
| Implement the algorithm: IDDFS with backtracking | [7. Algorithm](#7-algorithm-iddfs-with-backtracking) |

---

## 3. Problem Model

The problem is modelled as a **Constraint Satisfaction Problem (CSP)** and solved as a search problem.

| Element | Definition |
|---|---|
| **State** | A partially filled grid |
| **Initial state** | First row and first column fixed as `1 2 … n`; all other cells empty |
| **Action** | Place a number 1 … n in the next empty cell (row by row) |
| **Goal test** | All cells are filled and no number repeats in any row or column |
| **Path cost** | Each action costs 1. Every solution lies at depth (n − 1)² |

**Symmetry breaking.** The first row and the first column are fixed as `1 2 … n`. Every Latin square can be transformed into this form by renaming the numbers and reordering the rows, so **no solution is lost**. A square in this form is called a *reduced* Latin square.

---

## 4. Representation

### Variables

```
x[r][c]     r = 0 … n−1 (row),  c = 0 … n−1 (column)
```

There are n² variables, one per cell. After fixing the first row and column, **(n − 1)²** variables remain to be assigned, for example 16 when n = 5.

### Domain

```
D(x[r][c]) = {1, 2, …, n}
```

### Constraints

| | Constraint |
|---|---|
| C1 | Each **row** contains the numbers 1 … n exactly once |
| C2 | Each **column** contains the numbers 1 … n exactly once |

### Main Elements in the Code

| Name | Purpose |
|---|---|
| `grid[r][c]` | The number in row r, column c (0 = empty) |
| `cells` | The empty cells, in the order they are filled |
| `can_place(r, c, v)` | Checks whether v can be placed without violating C1 or C2 |
| `dls(i, limit)` | Depth-limited DFS; returns *found*, *cutoff* or *failure* |
| `iddfs()` | Calls `dls` with limit 0, 1, 2, … |
| `dfs()` | Plain DFS without a depth limit, used for comparison |

---

## 5. Objective Function

The objective function counts the **repeated numbers** in rows and columns:

```
f(S) =  Σ  ( n − number of distinct values in row r )
        r
      + Σ  ( n − number of distinct values in column c )
        c
```

- **f(S) = 0** means S is a valid Latin square.
- Goal: find a complete grid S with **f(S) = 0**.

In the code this is `objective_function(grid)`. Every solution is verified with it and the program prints `f(S) = 0`.

---

## 6. Landscape

All values below are printed by `python3 latin_square.py 5 --landscape`.

### Size of the Search Space for n = 5

| Representation | Formula | Size |
|---|---|---|
| Naive: every cell 1 … n | n^(n²) = 5²⁵ | 2.98 × 10¹⁷ |
| Every row a permutation | (n!)ⁿ = 120⁵ | 2.49 × 10¹⁰ |
| First row and column fixed | (n−1)^((n−1)²) = 4¹⁶ | 4.29 × 10⁹ |

Only **161,280** Latin squares of order 5 exist, and only **56** of them are in reduced form.

### Comparison for Different n

| n | Naive space n^(n²) | Latin squares that exist |
|---|---|---|
| 2 | 16 | 2 |
| 3 | 1.97 × 10⁴ | 12 |
| 4 | 4.29 × 10⁹ | 576 |
| 5 | 2.98 × 10¹⁷ | 161,280 |
| 6 | 1.03 × 10²⁸ | 812,851,200 |
| 7 | 2.57 × 10⁴¹ | 6.15 × 10¹³ |
| 8 | 6.28 × 10⁵⁷ | 1.09 × 10²⁰ |

(Number of Latin squares: OEIS A002860.)

### Shape of the Search Tree

- **Depth:** (n − 1)². Each level fills one cell.
- **Branching:** the number of values that can go into the next cell, at most n − 1.
- **Solutions:** all solutions lie at the **deepest level**, depth (n − 1)². This property is important for understanding the behaviour of IDDFS below.

---

## 7. Algorithm: IDDFS with Backtracking

### Approach

**Iterative Deepening DFS** runs a depth-limited DFS (**DLS**) repeatedly, with the depth limit increased by one each time:

1. Run DLS with limit 0. If no solution is found, continue.
2. Run DLS with limit 1, then 2, 3, …
3. Stop when DLS finds a solution within the limit.

Each run of DLS returns one of three results:

| Result | Meaning | What IDDFS does |
|---|---|---|
| *found* | A complete square was reached | Stop and return the solution |
| *cutoff* | At least one branch was stopped by the depth limit, so a solution may exist deeper | Increase the limit and run again |
| *failure* | No branch reached the limit; the whole tree was explored | Stop: no solution exists |

**Backtracking:** a number that violates C1 or C2 is never placed. When no number fits in a cell, the search returns to the previous cell and tries its next value.

### Pseudocode

```
IDDFS():
    for limit = 0, 1, 2, …:
        result ← DLS(0, limit)
        if result = found:   return SOLUTION
        if result = failure: return "no solution"

DLS(i, limit):                                # i = number of cells filled
    if i = number of cells: return found      # the grid is complete
    if limit = 0:           return cutoff     # depth limit reached
    (r, c) ← cells[i]
    cutoff ← false
    for v = 1 … n:
        if v is not in row r and not in column c:
            grid[r][c] ← v                    # step forward
            result ← DLS(i + 1, limit − 1)
            if result = found:  return found
            if result = cutoff: cutoff ← true
            grid[r][c] ← 0                    # backtrack
    return cutoff if cutoff else failure
```

### Why IDDFS, and Where It Falls Short

IDDFS combines the strengths of DFS and BFS:
- **Memory like DFS:** it stores only the current path, not an entire level as BFS does in the Sudoku problem.
- **Completeness and optimality like BFS:** because it tries the depths in order, it finds the shallowest solution.

For Latin squares, however, every solution lies at depth (n − 1)². All iterations with a smaller limit are guaranteed to fail, and their work is repeated at every new limit. The results below show this cost directly. IDDFS is the right choice when the depth of the solution is unknown and may be small; here the depth is known in advance.

---

## 8. Results

### IDDFS for n = 5, Nodes per Iteration

| Limit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | **16** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Nodes | 1 | 5 | 14 | 28 | 39 | 64 | 125 | 201 | 247 | 323 | 433 | 569 | 625 | 681 | 737 | 793 | **29** |

- Iterations 0–15 explore **4,885 nodes** and find nothing, because the solution lies deeper.
- The final iteration (limit 16) finds the solution after only **29 nodes**.
- Total: **4,914 nodes in 0.04 s**. About 99% of the work is spent in the earlier iterations.

### IDDFS and Plain DFS for Different n

| n | Depth of the solution | IDDFS nodes | IDDFS time | Plain DFS nodes | Plain DFS time |
|---|---|---|---|---|---|
| 2 | 1 | 3 | < 0.01 s | 2 | < 0.01 s |
| 3 | 4 | 19 | < 0.01 s | 6 | < 0.01 s |
| 4 | 9 | 161 | < 0.01 s | 10 | < 0.01 s |
| 5 | 16 | 4,914 | 0.04 s | 29 | < 0.01 s |
| 6 | 25 | 1,194,077 | 5.0 s | 52 | < 0.01 s |
| 7 | 36 | not found within 60 s (stopped at limit 18, about 16 million nodes) | — | 119 | < 0.01 s |
| 10 | 81 | not attempted | — | 1,446 | 0.02 s |

**Conclusion:** IDDFS with backtracking solves the Latin square up to n = 6. From n = 7 the repeated shallow iterations grow so large that IDDFS does not finish within the time limit. Plain DFS with the same backtracking and symmetry breaking finds a solution almost immediately, because it goes straight to the depth where all solutions lie. The difference, 29 nodes against 4,914 for n = 5 and 52 against 1.2 million for n = 6, is exactly the cost of re-exploring the shallow levels.

---

## 9. How to Run

From this folder:

```bash
python3 latin_square.py                  # n = 5: landscape, IDDFS and DFS comparison
python3 latin_square.py 6                # another size
python3 latin_square.py 5 --landscape    # landscape only
python3 latin_square.py 7 --time 120     # change the time limit
```

| Option | Description | Default |
|---|---|---|
| `n` | size of the square | 5 |
| `--landscape` | print only the landscape | off |
| `--time` | time limit for IDDFS and DFS, in seconds | 60 |
