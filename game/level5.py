import random
import sys
import time
import copy
from collections import deque
from pathlib import Path
import tkinter as tk

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from game.maps import Maps
    from game.renderer import Renderer
else:
    from .maps import Maps
    from .renderer import Renderer


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


class Level5:
    """Level 5: CSP path finding with Backtracking, Min-Conflicts, and AC-3."""

    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Level 5 - CSP Search")

        window_width = 1050
        window_height = 820
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid = Maps.get_level(5)
        self.original_grid = copy.deepcopy(self.grid)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.start = self._find_marker("S")
        self.goal = self._find_marker("D")
        self.actual_position = self.start

        self.algorithm = tk.StringVar(value="Backtracking")
        self.variables_var = tk.StringVar(value="10")

        self.csp = None
        self.solution_path = []
        self.animation_index = 0
        self.animation_running = False
        self.animation_timer_id = None
        self.execution_time = 0.0
        self.current_algorithm = "Backtracking"
        self.current_message = "Ready..."
        self.domain_summary = []

        self.BG = "#202225"
        self.PANEL = "#2F3136"
        self.BUTTON = "#5865F2"
        self.BUTTON_HOVER = "#4752C4"
        self.TEXT = "white"
        self.window.configure(bg=self.BG)

        self.main_frame = tk.Frame(self.window, bg=self.BG)
        self.main_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.cols * 64,
            height=self.rows * 64,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side="left", padx=10, pady=10)
        self.renderer = Renderer(self.canvas)

        self.control_frame = tk.Frame(self.main_frame, bg=self.PANEL, width=220)
        self.control_frame.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.control_frame.pack_propagate(False)

        tk.Label(
            self.control_frame,
            text="AI Controls",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(20, 15))

        tk.Label(
            self.control_frame,
            text="Algorithm",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(8, 4))

        algo_menu = tk.OptionMenu(
            self.control_frame,
            self.algorithm,
            "Backtracking",
            "Min-Conflicts",
            "AC-3"
        )
        algo_menu.config(
            bg="#40444B",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=12,
            relief="flat"
        )
        algo_menu.pack(pady=6)

        tk.Label(
            self.control_frame,
            text="Number of Variables",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 4))

        self.variables_entry = tk.Entry(
            self.control_frame,
            textvariable=self.variables_var,
            font=("Segoe UI", 11),
            justify="center"
        )
        self.variables_entry.pack(pady=6, ipady=4, padx=20, fill="x")

        self.create_button("Run AI", self.run_ai)
        self.create_button("Reset", self.reset)
        self.create_button("Back To Menu", self.back_to_menu)

        stats_frame = tk.LabelFrame(
            self.control_frame,
            text="Statistics",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold")
        )
        stats_frame.pack(fill="x", padx=10, pady=20)

        self.info = tk.Label(
            stats_frame,
            text="Ready...",
            bg=self.PANEL,
            fg="white",
            justify="left",
            font=("Consolas", 9),
            anchor="w",
            wraplength=205
        )
        self.info.pack(padx=10, pady=10, fill="x")

        self.renderer.draw_map(self.grid)

    def _find_marker(self, marker):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == marker:
                    return (r, c)
        raise ValueError(f"Marker {marker!r} not found in map")

    def create_button(self, text, command):
        btn = tk.Button(
            self.control_frame,
            text=text,
            command=command,
            bg=self.BUTTON,
            fg="white",
            activebackground=self.BUTTON_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            width=16,
            height=2,
            font=("Segoe UI", 10, "bold")
        )
        btn.pack(pady=8)
        return btn

    def _set_status(self, text):
        self.current_message = text
        self.info.config(text=text)
        self.window.update_idletasks()

    def _format_stats(self):
        path_length = len(self.solution_path)
        return (
            f"Algorithm : {self.current_algorithm}\n\n"
            f"Expanded Nodes   : {self.csp.expanded_nodes if self.csp else 0}\n"
            f"Assignments      : {self.csp.assignments if self.csp else 0}\n"
            f"Constraint Checks: {self.csp.constraint_checks if self.csp else 0}\n"
            f"Backtracks       : {self.csp.backtracks if self.csp else 0}\n"
            f"Execution Time   : {self.execution_time:.6f}s\n"
            f"Total Path Length: {path_length}"
        )

    def reset(self):
        self.cancel_animation()
        self.grid = copy.deepcopy(self.original_grid)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.start = self._find_marker("S")
        self.goal = self._find_marker("D")
        self.actual_position = self.start
        self.csp = None
        self.solution_path = []
        self.animation_index = 0
        self.animation_running = False
        self.animation_timer_id = None
        self.execution_time = 0.0
        self.current_algorithm = "Backtracking"
        self.domain_summary = []
        self.renderer.draw_map(self.grid)
        self._set_status("Ready...")

    def back_to_menu(self):
        self.cancel_animation()
        self.window.destroy()
        self.root.deiconify()

    def cancel_animation(self):
        if self.animation_timer_id is not None:
            try:
                self.window.after_cancel(self.animation_timer_id)
            except Exception:
                pass
            self.animation_timer_id = None
        self.animation_running = False

    def run_ai(self):
        raw_value = self.variables_var.get().strip()
        try:
            num_variables = int(raw_value)
        except ValueError:
            self._set_status("Please enter a valid integer for Number of Variables.")
            return

        if num_variables < 2:
            self._set_status("Number of Variables must be at least 2.")
            return

        self.cancel_animation()
        self.grid = copy.deepcopy(self.original_grid)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.start = self._find_marker("S")
        self.goal = self._find_marker("D")
        self.renderer.draw_map(self.grid)
        self.actual_position = self.start
        self.solution_path = []
        self.animation_index = 0
        self.domain_summary = []

        self.current_algorithm = self.algorithm.get()
        self.csp = PathCSP(self.grid, num_variables)

        feasible, reason = self.csp.path_length_is_feasible()
        if not feasible:
            self.execution_time = 0.0
            self.info.config(text=reason)
            return

        self._set_status(f"Solving with {self.current_algorithm}...")
        self.window.update_idletasks()

        start_time = time.perf_counter()
        path = None

        if self.current_algorithm == "Backtracking":
            path = self.csp.solve_backtracking(report=self._set_status)
        elif self.current_algorithm == "Min-Conflicts":
            path = self.csp.solve_min_conflicts(report=self._set_status)
        else:
            path, domains = self.csp.solve_ac3_then_backtracking(report=self._set_status)
            self.domain_summary = list(self.csp.domain_reductions)
            if domains is not None and not path:
                path = None

        self.execution_time = time.perf_counter() - start_time

        if not path:
            self.solution_path = []
            self.info.config(text=self._format_failure_text())
            return

        self.solution_path = path
        self.actual_position = self.solution_path[0]
        self.render_scene()
        self.animation_running = True
        self.animation_index = 0
        self._set_status("Animating solution...")
        self._schedule_next_step()

    def _format_failure_text(self):
        domain_note = ""
        if self.domain_summary:
            domain_note = "\n" + "\n".join(self.domain_summary[:6])
        return (
            f"No solution found.\n\n"
            f"Algorithm : {self.current_algorithm}\n"
            f"Time : {self.execution_time:.6f}s\n"
            f"Expanded Nodes : {self.csp.expanded_nodes if self.csp else 0}\n"
            f"Assignments : {self.csp.assignments if self.csp else 0}\n"
            f"Constraint Checks : {self.csp.constraint_checks if self.csp else 0}\n"
            f"Backtracks : {self.csp.backtracks if self.csp else 0}"
            f"{domain_note}"
        )

    def _schedule_next_step(self):
        if not self.animation_running:
            return
        self.animation_timer_id = self.window.after(150, self._play_next_step)

    def _play_next_step(self):
        if not self.animation_running:
            return

        if self.animation_index >= len(self.solution_path):
            self.animation_running = False
            self.animation_timer_id = None
            self.info.config(text=self._format_stats())
            return

        self.actual_position = self.solution_path[self.animation_index]
        self._dig_trail(self.actual_position)
        self.render_scene()
        self._set_status(
            f"Animating step {self.animation_index + 1}/{len(self.solution_path)}"
        )
        self.animation_index += 1
        self._schedule_next_step()

    def _dig_trail(self, position):
        row, col = position
        if self.grid[row][col] in (1, 1.5, 2, 3):
            self.grid[row][col] = 0

    def render_scene(self):
        self.renderer.draw_map(self.grid)
        self.draw_variable_labels()
        self.draw_player()

    def draw_variable_labels(self):
        self.canvas.delete("labels")
        if not self.solution_path:
            return

        labels = self.csp.variable_labels(self.solution_path) if self.csp else {}
        for (row, col), label in labels.items():
            self.canvas.create_text(
                col * 64 + 32,
                row * 64 + 48,
                text=label,
                fill="#FFFFFF",
                font=("Segoe UI", 10, "bold"),
                tags="labels"
            )

    def draw_player(self):
        self.canvas.delete("steve")
        self.canvas.create_image(
            self.actual_position[1] * 64,
            self.actual_position[0] * 64,
            image=self.renderer.steve_img,
            anchor="nw",
            tags="steve"
        )

    def on_close(self):
        self.cancel_animation()
        self.window.destroy()
        self.root.deiconify()
