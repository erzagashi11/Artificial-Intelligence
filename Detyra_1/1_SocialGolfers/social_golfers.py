"""
Social Golfers Problem: Depth-First Search with Backtracking

32 golfers play every week in 8 groups of 4. Two golfers who have already
played in the same group must never be grouped together again.
Question: for how many weeks can this go on?

Usage:
    python social_golfers.py               # landscape + as many weeks as possible
    python social_golfers.py --w 7         # exactly 7 weeks
    python social_golfers.py --fixed       # fixed ordering (no random seed)
    python social_golfers.py --landscape   # landscape only
    python social_golfers.py --g 5 --p 3   # 15 golfers in groups of 3
"""

import argparse
import math
import random
import time
from itertools import combinations


# ---------------------------------------------------------------------
#  Default parameters (can be changed from the command line)
# ---------------------------------------------------------------------
DEFAULT_GROUPS = 8          # groups per week
DEFAULT_GROUP_SIZE = 4      # golfers per group
DEFAULT_SEED = 1            # random ordering of candidates; None = fixed order
DEFAULT_TIME_LIMIT = 20     # seconds allowed for one number of weeks


class SocialGolfers:
    """
    Representation:
        schedule[w]  = list of groups in week w, e.g. [[0, 1, 2, 3], [4, 5, 6, 7], ...]
        met[a][b]    = True if golfers a and b have already played in the same group
    """

    def __init__(self, groups, group_size, seed=DEFAULT_SEED, time_limit=DEFAULT_TIME_LIMIT):
        self.groups = groups
        self.group_size = group_size
        self.players = groups * group_size
        self.seed = seed
        self.time_limit = time_limit

        self.schedule = []
        self.met = []
        self.nodes = 0          # number of groups tried in total
        self.start_time = 0.0
        self.rng = None

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def mark_group(self, group, value):
        """value=True: every pair in the group has now met. value=False: undo (backtrack)."""
        for a in group:
            for b in group:
                if a != b:
                    self.met[a][b] = value

    def is_fresh_group(self, group):
        """True if no pair in the group has met before (constraint 3)."""
        return all(not self.met[a][b] for a, b in combinations(group, 2))

    def forward_check(self, remaining):
        """
        Pruning: every golfer still without a group this week must have at
        least (group_size - 1) possible partners among the remaining golfers.
        If not, this branch cannot lead to a solution.
        """
        for a in remaining:
            free_partners = sum(1 for b in remaining if b != a and not self.met[a][b])
            if free_partners < self.group_size - 1:
                return False
        return True

    def time_is_up(self):
        return time.time() - self.start_time > self.time_limit

    def elapsed(self):
        return time.time() - self.start_time

    # ------------------------------------------------------------------
    #  DFS with backtracking
    # ------------------------------------------------------------------
    def dfs(self, week, remaining, num_weeks):
        """
        Fills week `week` one group at a time.
        `remaining` = golfers who do not have a group yet in this week.
        Returns True once the full schedule has been found.
        """
        if self.time_is_up():
            return False

        # Week is complete: move on to the next week (or finish)
        if not remaining:
            if week == num_weeks - 1:
                return True
            return self.dfs(week + 1, list(range(self.players)), num_weeks)

        # The lowest-numbered remaining golfer opens the new group
        anchor = remaining[0]

        # Possible partners: remaining golfers the anchor has not met yet
        candidates = [x for x in remaining[1:] if not self.met[anchor][x]]
        if self.rng is not None:
            self.rng.shuffle(candidates)

        # Try every combination of (group_size - 1) partners
        for partners in combinations(candidates, self.group_size - 1):
            self.nodes += 1
            group = sorted([anchor, *partners])

            if not self.is_fresh_group(group):
                continue

            # Step forward: place the group
            self.schedule[week].append(group)
            self.mark_group(group, True)
            still_remaining = [x for x in remaining if x not in group]

            # Go deeper
            if self.forward_check(still_remaining) and self.dfs(week, still_remaining, num_weeks):
                return True

            # Backtrack: undo the group and try the next combination
            self.mark_group(group, False)
            self.schedule[week].pop()

        return False

    def solve(self, num_weeks):
        """Searches for a schedule of `num_weeks` weeks. Returns True if one is found."""
        self.schedule = [[] for _ in range(num_weeks)]
        self.met = [[False] * self.players for _ in range(self.players)]
        self.nodes = 0
        self.start_time = time.time()
        self.rng = random.Random(self.seed) if self.seed is not None else None

        # Symmetry breaking: week 1 is fixed as [0,1,2,3], [4,5,6,7], ...
        for g in range(self.groups):
            group = list(range(g * self.group_size, (g + 1) * self.group_size))
            self.schedule[0].append(group)
            self.mark_group(group, True)

        if num_weeks == 1:
            return True
        return self.dfs(1, list(range(self.players)), num_weeks)

    # ------------------------------------------------------------------
    #  Objective function and verification
    # ------------------------------------------------------------------
    @staticmethod
    def objective_function(schedule):
        """
        f(S) = number of repeated meetings in the schedule.
        f(S) = 0 means the schedule is valid.
        """
        times_met = {}
        for week in schedule:
            for group in week:
                for a, b in combinations(group, 2):
                    pair = (min(a, b), max(a, b))
                    times_met[pair] = times_met.get(pair, 0) + 1
        return sum(count - 1 for count in times_met.values() if count > 1)

    def verify(self, schedule):
        """Checks all three constraints."""
        for week in schedule:
            # Constraint 1: every golfer plays exactly once per week
            if sorted(x for group in week for x in group) != list(range(self.players)):
                return False
            # Constraint 2: every group has exactly group_size golfers
            if any(len(group) != self.group_size for group in week):
                return False
        # Constraint 3: no pair meets twice
        return self.objective_function(schedule) == 0

    # ------------------------------------------------------------------
    #  Landscape
    # ------------------------------------------------------------------
    def landscape(self):
        n, g, p = self.players, self.groups, self.group_size
        max_weeks = (n - 1) // (p - 1)

        print("=== LANDSCAPE ===\n")

        # 1) Theoretical upper bound
        print(f"Total pairs:              C({n},2) = {n * (n - 1) // 2}")
        print(f"New pairs per week:       {g} * C({p},2) = {g * p * (p - 1) // 2}")
        print(f"Theoretical upper bound:  ({n}-1) / ({p}-1) = {max_weeks} weeks\n")

        # 2) Size of the search space for ONE week, in three representations
        naive = n ** n
        permutations = math.factorial(n)
        one_week = math.factorial(n) // (math.factorial(p) ** g * math.factorial(g))
        print("Search space for ONE week:")
        print(f"  a) naive ({n} variables, domain {n}):    {n}^{n} = {naive:.3e}")
        print(f"  b) permutations only:                {n}!  = {permutations:.3e}")
        print(f"  c) partition into groups (no symmetry): {one_week:.3e}\n")

        # 3) Branching factor of the tree for each group of a week
        print("Branching factor (combinations for each group of the week):")
        branching = [math.comb(n - i * p - 1, p - 1) for i in range(g)]
        print("  " + " * ".join(str(b) for b in branching) + f" = {math.prod(branching):.3e}\n")

        # 4) Search space for w weeks (week 1 fixed)
        print("Search space for w weeks (week 1 fixed):")
        for w in range(1, max_weeks + 1):
            print(f"  w = {w:2d}:  {one_week ** (w - 1):.3e}")
        print()


# ---------------------------------------------------------------------
#  Output
# ---------------------------------------------------------------------
def print_schedule(schedule):
    for i, week in enumerate(schedule, 1):
        row = " | ".join(",".join(f"{x:2d}" for x in group) for group in week)
        print(f"Week {i:2d}:  {row}")


def print_result(solver, schedule):
    print_schedule(schedule)
    f = solver.objective_function(schedule)
    print(f"\nObjective function f(S) = {f}  (0 = no repeated pair)")
    print(f"Verification (3 constraints): {'OK' if solver.verify(schedule) else 'FAILED'}")


# ---------------------------------------------------------------------
#  Main program
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Social Golfers: DFS with backtracking")
    parser.add_argument("--g", type=int, default=DEFAULT_GROUPS, help="groups per week (default 8)")
    parser.add_argument("--p", type=int, default=DEFAULT_GROUP_SIZE, help="golfers per group (default 4)")
    parser.add_argument("--w", type=int, default=None, help="search for exactly W weeks")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="seed for random ordering (default 1)")
    parser.add_argument("--fixed", action="store_true", help="fixed ordering 0,1,2,... (no seed)")
    parser.add_argument("--time", type=float, default=DEFAULT_TIME_LIMIT,
                        help="seconds allowed per number of weeks (default 20)")
    parser.add_argument("--landscape", action="store_true", help="print the landscape only")
    args = parser.parse_args()

    solver = SocialGolfers(
        groups=args.g,
        group_size=args.p,
        seed=None if args.fixed else args.seed,
        time_limit=args.time,
    )
    header = f"{solver.players} golfers, {solver.groups} groups x {solver.group_size}"

    # Landscape only
    if args.landscape:
        solver.landscape()
        return

    # Exactly W weeks
    if args.w is not None:
        print(f"=== DFS: {args.w} weeks ({header}) ===")
        found = solver.solve(args.w)
        status = "FOUND" if found else "NOT FOUND"
        print(f"{status} ({solver.nodes} nodes, {solver.elapsed():.2f} s)\n")
        if found:
            print_result(solver, solver.schedule)
        return

    # Default: landscape + as many weeks as possible
    solver.landscape()
    print(f"=== DFS WITH BACKTRACKING ({header}) ===")
    best = None
    max_weeks = (solver.players - 1) // (solver.group_size - 1)

    # Try 1 week, 2 weeks, 3 weeks, ... until DFS fails
    for num_weeks in range(1, max_weeks + 1):
        found = solver.solve(num_weeks)
        status = "FOUND    " if found else "NOT FOUND"
        print(f"{num_weeks:2d} weeks: {status} ({solver.nodes} nodes, {solver.elapsed():.2f} s)")
        if not found:
            break
        best = solver.schedule

    print(f"\nAnswer: {len(best)} weeks\n")
    print_result(solver, best)


if __name__ == "__main__":
    main()
