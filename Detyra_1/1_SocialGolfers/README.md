# Social Golfers Problem: Depth-First Search with Backtracking

Implementation: [`social_golfers.py`](social_golfers.py) (Python 3.8+, standard library only)

---

## 1. Problem Statement

A golf club has **32 members** who play once a week, always split into **8 groups of 4**. The club wants to vary the groups as much as possible: two golfers who have already played in the same group should never be placed together again.

**Question:** for how many weeks can such a schedule be maintained?

In general form, the problem is written as **SGP(g, p, w)**: schedule n = g · p golfers in g groups of p golfers for w weeks, so that every golfer plays exactly once per week and no pair of golfers shares a group more than once. The instance in this assignment is **g = 8, p = 4 (n = 32)**, and the task is to find the largest w.

---

## 2. Assignment Requirements

| Requirement | Section |
|---|---|
| Model the problem | [3. Problem Model](#3-problem-model) |
| Describe the representation (variables, domain, constraints) | [4. Representation](#4-representation) |
| Formulate the objective function | [5. Objective Function](#5-objective-function) |
| Calculate the landscape | [6. Landscape](#6-landscape) |
| Implement the algorithm: DFS with backtracking | [7. Algorithm](#7-algorithm-dfs-with-backtracking) |

---

## 3. Problem Model

The problem is modelled as a **Constraint Satisfaction Problem (CSP)** and solved as a search problem.

| Element | Definition |
|---|---|
| **State** | A partially built schedule: some weeks and groups are filled, the rest are empty |
| **Initial state** | Week 1 fixed as `{0,1,2,3}, {4,5,6,7}, …, {28,29,30,31}`; all other weeks empty |
| **Action** | Add one new group of p golfers to the current week |
| **Goal test** | All w weeks are complete and no pair of golfers has met twice |
| **Path cost** | Not relevant: only the existence of a valid schedule matters |

**Symmetry breaking.** Many schedules are identical up to renaming golfers or reordering groups. Three rules remove these duplicates without losing any solution:

1. **Week 1 is fixed.** Any valid schedule can be relabelled so that week 1 is `{0..3}, {4..7}, …`.
2. **Group order inside a week.** A new group is always opened by the lowest-numbered golfer who has no group yet (the *anchor*).
3. **Golfer order inside a group.** Partners are chosen as combinations, not permutations.

---

## 4. Representation

### Variables

```
x[w][g][s]     w = 0 … W−1   (week)
               g = 0 … 7     (group)
               s = 0 … 3     (seat in the group)
```

`x[w][g][s]` is the golfer who plays in week w, group g, seat s. There are W · g · p = 32 · W variables. The search assigns them **one group at a time** (four variables per step).

### Domain

```
D(x[w][g][s]) = {0, 1, …, 31}
```

### Constraints

| | Constraint | Formal statement |
|---|---|---|
| C1 | Each golfer plays exactly once per week | for every week w, the values x[w][·][·] form a permutation of {0, …, 31} |
| C2 | Each group has exactly p = 4 golfers | guaranteed by the structure of x |
| C3 | No pair of golfers meets more than once | for every a ≠ b: \|{(w, g) : a, b ∈ group(w, g)}\| ≤ 1 |

### Data Structures in the Code

| Name | Meaning |
|---|---|
| `schedule[w][g]` | the golfers of week w, group g |
| `met[a][b]` | `True` if golfers a and b have already played together (checks C3 in O(1)) |
| `remaining` | golfers without a group in the current week (enforces C1) |
| `anchor` | the lowest-numbered golfer in `remaining`; opens the next group |
| `nodes` | number of groups tried, i.e. nodes of the search tree |

---

## 5. Objective Function

Because C1 and C2 are guaranteed by the representation, the objective function counts only violations of C3, the repeated meetings:

```
f(S) =  Σ    max(0, meetings(a, b) − 1)
       a < b

meetings(a, b) = number of groups in S that contain both a and b
```

- **f(S) = 0**: S is a valid schedule.
- **f(S) > 0**: the value is the number of repeated meetings.

The assignment question is therefore the optimisation problem

```
maximise W   subject to   there exists a schedule S with W weeks and f(S) = 0
```

In the code this is `SocialGolfers.objective_function(schedule)`. Every solution is verified with it and the program prints `f(S) = 0`.

### Theoretical Upper Bound

Each week a golfer meets p − 1 = 3 new partners, and there are only n − 1 = 31 other golfers:

```
W ≤ ⌊(n − 1) / (p − 1)⌋ = ⌊31 / 3⌋ = 10 weeks
```

Counting pairs gives the same result: C(32, 2) = 496 pairs in total and 8 · C(4, 2) = 48 new pairs per week, so at most ⌊496 / 48⌋ = 10 weeks. A 10-week schedule is known to exist, but it was found with specialised constructive methods, not with uninformed search.

---

## 6. Landscape

All values below are printed by `python3 social_golfers.py --landscape`.

### Size of the Search Space for One Week

| Representation | Formula | Size |
|---|---|---|
| Naive: 32 variables with domain 32 | 32³² | 1.46 × 10⁴⁸ |
| Permutations only (C1 enforced) | 32! | 2.63 × 10³⁵ |
| Partitions into groups (order removed) | 32! / ((4!)⁸ · 8!) | 5.93 × 10¹⁹ |

The last representation, P = 5.93 × 10¹⁹, is exactly what the DFS generates. The branching factor of each group in a week is:

| Group | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Choices | C(31,3) = 4495 | C(27,3) = 2925 | C(23,3) = 1771 | C(19,3) = 969 | C(15,3) = 455 | C(11,3) = 165 | C(7,3) = 35 | C(3,3) = 1 |

The product of these values is again 5.93 × 10¹⁹.

### Size of the Search Space for W Weeks

With week 1 fixed, the space grows as P^(W−1):

| W | 2 | 3 | 5 | 7 | 8 | 10 |
|---|---|---|---|---|---|---|
| Size | 5.93 × 10¹⁹ | 3.52 × 10³⁹ | 1.24 × 10⁷⁹ | 4.34 × 10¹¹⁸ | 2.58 × 10¹³⁸ | 9.05 × 10¹⁷⁷ |

### Shape of the Search Tree

- **Depth:** (W − 1) · g levels, e.g. 56 levels for W = 8.
- **Branching:** 4495 at the first group of a week, decreasing to 1 at the last group.
- **Solutions:** only at the deepest level, and extremely rare compared to the size of the space. Pruning is therefore essential.

---

## 7. Algorithm: DFS with Backtracking

### Approach

The schedule is built **week by week** and, inside each week, **group by group**. At every node the DFS takes the anchor (the lowest free golfer), tries every combination of three partners the anchor has not met, places the group and goes one level deeper. If a branch cannot be completed, the last group is removed (**backtracking**) and the next combination is tried.

To answer the assignment question, the program runs this search for W = 1, 2, 3, … and stops at the first W for which no schedule is found within the time limit.

### Pseudocode

```
DFS(week, remaining):
    if remaining is empty:                        # current week is complete
        if week == W − 1: return TRUE             # all weeks are complete
        return DFS(week + 1, {0, …, n−1})

    anchor ← min(remaining)
    candidates ← golfers in remaining that anchor has not met

    for each combination {b, c, d} of candidates:
        if any pair in {anchor, b, c, d} has met before: continue      # C3
        place the group and mark its pairs as met
        rest ← remaining − group
        if forward_check(rest) and DFS(week, rest): return TRUE
        remove the group and unmark its pairs                          # backtrack
    return FALSE
```

### Techniques Used

| Technique | Purpose | Function in the code |
|---|---|---|
| Symmetry breaking | Avoids exploring equivalent schedules | `solve`, `dfs` |
| Constraint check (C3) | Rejects a group whose golfers have already met | `is_fresh_group` |
| Forward checking | Cuts a branch as soon as a remaining golfer has fewer than p − 1 possible partners | `forward_check` |
| Backtracking | Undoes the last group and tries the next combination | `mark_group(group, False)` |
| Random child ordering | Tries the children of each node in a seeded random order; the search is still a complete DFS | `self.rng.shuffle(candidates)` |

**Why random ordering.** With a fixed order (0, 1, 2, …), the DFS first builds schedules in which golfers 0–15 and 16–31 only ever play within their own half. Such a schedule can last at most 5 weeks, and the DFS then spends a very long time in that dead subtree. A seeded random order mixes the groups from the start and avoids this trap. The seed makes every run reproducible.

---

## 8. Results

Instance g = 8, p = 4 (32 golfers), time limit 20 s for each W:

| W | Random ordering (seed 1, default) | Fixed ordering (`--fixed`) |
|---|---|---|
| 1–5 | found, < 0.01 s | found, < 0.01 s |
| 6 | found, 3,378 nodes, 0.01 s | not found within 20 s (10.5 million nodes) |
| 7 | **found, 156,325 nodes, 0.4 s** | not attempted |
| 8 | not found within 20 s (7.4 million nodes) | not attempted |

**Answer: 7 weeks.** DFS with backtracking finds a valid 7-week schedule out of a theoretical maximum of 10. For 8 weeks and beyond the search space exceeds 10¹³⁸ and uninformed search no longer completes in reasonable time.

7-week schedule found with seed 1 (verified, f(S) = 0):

```
Week 1: { 0, 1, 2, 3}  { 4, 5, 6, 7}  { 8, 9,10,11}  {12,13,14,15}  {16,17,18,19}  {20,21,22,23}  {24,25,26,27}  {28,29,30,31}
Week 2: { 0,15,27,30}  { 1, 5, 8,13}  { 2, 7,22,31}  { 3,11,21,29}  { 4,14,19,24}  { 6,17,23,28}  { 9,12,16,25}  {10,18,20,26}
Week 3: { 0, 7, 8,20}  { 1, 6,14,21}  { 2,11,12,18}  { 3, 5,16,22}  { 4,10,27,29}  { 9,15,24,28}  {13,17,25,31}  {19,23,26,30}
Week 4: { 0,18,22,24}  { 1, 4, 9,30}  { 2,16,20,28}  { 3,10,23,25}  { 5,15,21,31}  { 6,13,19,29}  { 7,11,14,26}  { 8,12,17,27}
Week 5: { 0,10,14,28}  { 1,20,24,31}  { 2, 5,23,27}  { 3, 4,13,18}  { 6,12,22,26}  { 7, 9,17,29}  { 8,16,21,30}  {11,15,19,25}
Week 6: { 0,13,21,26}  { 1,11,22,28}  { 2, 6,24,30}  { 3, 9,27,31}  { 4,15,16,23}  { 5,14,17,20}  { 7,10,12,19}  { 8,18,25,29}
Week 7: { 0, 5, 9,19}  { 1,12,23,29}  { 2,10,17,21}  { 3, 6,15,20}  { 4, 8,26,31}  { 7,18,27,28}  {11,13,16,24}  {14,22,25,30}
```

---

## 9. How to Run

From this folder:

```bash
python3 social_golfers.py               # landscape + maximum number of weeks
python3 social_golfers.py --w 7         # search for exactly 7 weeks
python3 social_golfers.py --fixed       # fixed child ordering (no seed)
python3 social_golfers.py --landscape   # landscape only
python3 social_golfers.py --g 5 --p 3   # another instance: 15 golfers in groups of 3
```

| Option | Description | Default |
|---|---|---|
| `--g` | number of groups per week | 8 |
| `--p` | golfers per group | 4 |
| `--w` | search for exactly W weeks instead of the maximum | none |
| `--seed` | seed for the random child ordering | 1 |
| `--fixed` | use the fixed order 0, 1, 2, … instead of a seed | off |
| `--time` | time limit per W, in seconds | 20 |
| `--landscape` | print only the landscape | off |
