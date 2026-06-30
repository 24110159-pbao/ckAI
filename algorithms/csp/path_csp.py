import random
from collections import deque


class PathCSP:
    """CSP solver for a fixed-length simple path from Steve to the diamond."""

    def __init__(self, grid, num_variables, allow_revisit=False):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.num_variables = num_variables
        self.allow_revisit = allow_revisit

        self.start = self._find_marker("S")
        self.goal = self._find_marker("D")
        self.walkable_positions = self._collect_walkable_positions()

        self.expanded_nodes = 0
        self.assignments = 0
        self.constraint_checks = 0
        self.backtracks = 0
        self.domain_reductions = []

    def reset_metrics(self):
        self.expanded_nodes = 0
        self.assignments = 0
        self.constraint_checks = 0
        self.backtracks = 0
        self.domain_reductions = []

    def _find_marker(self, marker):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == marker:
                    return (r, c)
        raise ValueError(f"Marker {marker!r} not found in map")

    def _collect_walkable_positions(self):
        positions = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != 4:
                    positions.append((r, c))
        return positions

    def in_bounds(self, cell):
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, cell):
        if not self.in_bounds(cell):
            return False
        return self.grid[cell[0]][cell[1]] != 4

    def manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adjacent(self, a, b):
        self.constraint_checks += 1
        return self.manhattan(a, b) == 1

    def neighbors(self, cell):
        row, col = cell
        candidates = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]
        return [pos for pos in candidates if self.is_walkable(pos)]

    def initial_domains(self):
        domains = []
        for index in range(self.num_variables):
            if index == 0:
                domains.append({self.start})
            elif index == self.num_variables - 1:
                domains.append({self.goal})
            else:
                domains.append(set(self.walkable_positions))
        return domains

    def path_length_is_feasible(self):
        moves = self.num_variables - 1
        shortest = self.manhattan(self.start, self.goal)
        walkable_count = len(self.walkable_positions)

        if self.num_variables > walkable_count:
            return False, (
                f"Requested path needs {self.num_variables} distinct cells but the map only has "
                f"{walkable_count} walkable cells."
            )
        if moves < shortest:
            return False, (
                f"Requested path needs at least {shortest + 1} variables "
                f"but you entered {self.num_variables}."
            )
        if (moves - shortest) % 2 != 0:
            return False, (
                "Requested number of variables has the wrong parity for this map. "
                "Try another value."
            )
        return True, ""

    def _future_reachable(self, cell, steps_left):
        """Necessary pruning for exact-length paths with 4-neighbor moves."""
        distance = self.manhattan(cell, self.goal)
        if distance > steps_left:
            return False
        return (steps_left - distance) % 2 == 0

    def _format_assignment(self, assignment, index, value):
        return f"X{index + 1} = {value}"

    def _variable_conflicts(self, index, value, assignment):
        conflicts = 0

        if index == 0:
            self.constraint_checks += 1
            return 0 if value == self.start else 1

        if index == self.num_variables - 1:
            self.constraint_checks += 1
            return 0 if value == self.goal else 1

        if not self.is_walkable(value):
            self.constraint_checks += 1
            conflicts += 1

        previous_value = assignment[index - 1]
        if previous_value is not None:
            if not self.adjacent(previous_value, value):
                conflicts += 1

        next_value = assignment[index + 1]
        if next_value is not None:
            if not self.adjacent(value, next_value):
                conflicts += 1

        if not self.allow_revisit:
            for other_index, other_value in enumerate(assignment):
                if other_index != index and other_value == value:
                    self.constraint_checks += 1
                    conflicts += 1
                    break

        return conflicts

    def _consistent_with_assignment(self, index, value, assignment):
        if not self.is_walkable(value):
            self.constraint_checks += 1
            return False

        if index == 0:
            self.constraint_checks += 1
            return value == self.start

        if index == self.num_variables - 1:
            self.constraint_checks += 1
            return value == self.goal

        previous_value = assignment[index - 1]
        if previous_value is not None:
            if not self.adjacent(previous_value, value):
                return False

        next_value = assignment[index + 1]
        if next_value is not None:
            if not self.adjacent(value, next_value):
                return False

        if not self.allow_revisit:
            for other_index, other_value in enumerate(assignment):
                if other_index != index and other_value == value:
                    self.constraint_checks += 1
                    return False

        return True

    def _ordered_candidates(self, index, assignment, domains):
        steps_left = (self.num_variables - 1) - index
        candidates = list(domains[index])

        previous_value = assignment[index - 1]
        if previous_value is not None:
            candidates = [cell for cell in candidates if self.adjacent(previous_value, cell)]

        candidates = [cell for cell in candidates if self._future_reachable(cell, steps_left)]

        if not candidates and previous_value is not None:
            candidates = [cell for cell in self.neighbors(previous_value) if self._future_reachable(cell, steps_left)]

        if not candidates:
            candidates = [
                cell for cell in self.walkable_positions
                if self._future_reachable(cell, steps_left)
            ]

        candidates.sort(
            key=lambda cell: (
                abs(self.manhattan(cell, self.goal) - steps_left),
                self.manhattan(cell, self.goal),
                cell[0],
                cell[1],
            )
        )
        return candidates

    def solve_backtracking(self, report=None, domains=None, reset_metrics=True):
        if reset_metrics:
            self.reset_metrics()
        report = report or (lambda message: None)

        assignment = [None] * self.num_variables
        assignment[0] = self.start
        assignment[-1] = self.goal
        self.assignments += 2
        report("X1 = start")
        report(f"X{self.num_variables} = goal")

        if domains is None:
            domains = self.initial_domains()

        solution = self._backtrack(1, assignment, domains, report)
        return solution

    def _backtrack(self, index, assignment, domains, report):
        self.expanded_nodes += 1

        if index == self.num_variables - 1:
            previous_value = assignment[index - 1]
            if previous_value is not None and self.adjacent(previous_value, self.goal):
                return assignment[:]
            self.backtracks += 1
            return None

        candidates = self._ordered_candidates(index, assignment, domains)
        for value in candidates:
            self.constraint_checks += 1
            if not self._consistent_with_assignment(index, value, assignment):
                continue

            assignment[index] = value
            self.assignments += 1
            report(self._format_assignment(assignment, index, value))

            result = self._backtrack(index + 1, assignment, domains, report)
            if result is not None:
                return result

            assignment[index] = None
            self.backtracks += 1
            report(f"Backtrack from X{index + 1}")

        return None

    def solve_min_conflicts(self, report=None, max_steps=5000, restart_limit=20):
        self.reset_metrics()
        report = report or (lambda message: None)

        for restart in range(restart_limit + 1):
            assignment = [None] * self.num_variables
            assignment[0] = self.start
            assignment[-1] = self.goal
            self.assignments += 2

            for index in range(1, self.num_variables - 1):
                assignment[index] = random.choice(self.walkable_positions)
                self.assignments += 1

            best_streak = 0

            for step in range(max_steps):
                self.expanded_nodes += 1

                conflicted = []
                for index in range(1, self.num_variables - 1):
                    if self._variable_conflicts(index, assignment[index], assignment) > 0:
                        conflicted.append(index)

                if not conflicted:
                    if self._variable_conflicts(self.num_variables - 2, assignment[-2], assignment) == 0:
                        return assignment

                if not conflicted:
                    break

                worst_index = max(
                    conflicted,
                    key=lambda idx: self._variable_conflicts(idx, assignment[idx], assignment)
                )

                current_conflicts = self._variable_conflicts(
                    worst_index,
                    assignment[worst_index],
                    assignment
                )

                candidates = self._repair_candidates(worst_index, assignment)
                scored_candidates = []
                for value in candidates:
                    score = self._variable_conflicts(worst_index, value, assignment)
                    scored_candidates.append((score, self.manhattan(value, self.goal), value))

                if not scored_candidates:
                    continue

                scored_candidates.sort(key=lambda item: (item[0], item[1], item[2][0], item[2][1]))
                best_score, _, best_value = scored_candidates[0]

                if best_score <= current_conflicts:
                    assignment[worst_index] = best_value
                    self.assignments += 1
                    best_streak = 0
                else:
                    assignment[worst_index] = best_value
                    self.assignments += 1
                    best_streak += 1

                if step % 25 == 0:
                    report(
                        f"Min-Conflicts restart {restart + 1}, step {step + 1}, "
                        f"repairing X{worst_index + 1}"
                    )

                if best_streak >= 150:
                    break

            report(f"Restarting min-conflicts ({restart + 1})")

        return None

    def _repair_candidates(self, index, assignment):
        left_value = assignment[index - 1] if index - 1 >= 0 else None
        right_value = assignment[index + 1] if index + 1 < self.num_variables else None

        if left_value is not None and right_value is not None:
            candidates = [
                cell for cell in self.walkable_positions
                if self.adjacent(left_value, cell) and self.adjacent(cell, right_value)
            ]
            if candidates:
                return candidates

        if left_value is not None:
            candidates = self.neighbors(left_value)
            if candidates:
                return candidates

        if right_value is not None:
            candidates = self.neighbors(right_value)
            if candidates:
                return candidates

        return list(self.walkable_positions)

    def variable_labels(self, path):
        labels = {}
        for index, cell in enumerate(path):
            labels[cell] = f"x{index + 1}"
        return labels

    def solve_ac3_then_backtracking(self, report=None):
        self.reset_metrics()
        report = report or (lambda message: None)

        domains = self.initial_domains()
        if not self._ac3(domains, report):
            return None, domains

        solution = self.solve_backtracking(
            report=report,
            domains=domains,
            reset_metrics=False
        )
        return solution, domains

    def _ac3(self, domains, report):
        queue = deque()
        for index in range(self.num_variables - 1):
            queue.append((index, index + 1))
            queue.append((index + 1, index))

        while queue:
            xi, xj = queue.popleft()
            self.expanded_nodes += 1
            if self._revise(xi, xj, domains, report):
                if not domains[xi]:
                    return False
                for xk in range(self.num_variables):
                    if xk != xi and xk != xj and abs(xk - xi) == 1:
                        queue.append((xk, xi))
        return True

    def _revise(self, xi, xj, domains, report):
        revised = False
        to_remove = set()

        for value in domains[xi]:
            self.constraint_checks += 1
            supported = False
            for other in domains[xj]:
                self.constraint_checks += 1
                if self.adjacent(value, other):
                    supported = True
                    break
            if not supported:
                to_remove.add(value)

        if to_remove:
            before_size = len(domains[xi])
            domains[xi] -= to_remove
            after_size = len(domains[xi])
            revised = True
            self.domain_reductions.append(
                f"X{xi + 1}: {before_size} -> {after_size}"
            )
            report(f"AC-3 pruned X{xi + 1}: {before_size} -> {after_size}")

        return revised

