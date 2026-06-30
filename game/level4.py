import os
import copy
import sys
import time
import random
import tkinter as tk
from collections import deque
from pathlib import Path
from PIL import Image, ImageTk

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from game.maps import Maps
    from game.renderer import Renderer
else:
    from .maps import Maps
    from .renderer import Renderer

from algorithms.complex.partial_observability import (
    BeliefState as POBeliefState,
    Level4Planner as POLevel4Planner,
    ObservationModel as POObservationModel,
    TransitionModel as POTransitionModel,
    VisibilityState as POVisibilityState,
    WorldState as POWorldState,
)


MODE_1 = "Sensorless Search"
MODE_AND_OR = "AND-OR Search"
MODE_3 = "Partially Observable"


class Level4:
    """Planning under partial observability with three observation modes."""

    def __init__(self, root):
        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Level 4 - Partial Observability")

        window_width = 1050
        window_height = 820
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.world_grid = Maps.get_level(4)
        self.original_world_grid = copy.deepcopy(self.world_grid)
        self.rows = len(self.world_grid)
        self.cols = len(self.world_grid[0])

        self.start = self._find_cell("S")
        self.goal = self._find_cell("D")
        self.actual_position = self.start

        self.transition_model = POTransitionModel()
        self.observation_model = POObservationModel()
        self.visibility_state = POVisibilityState(fog_radius=2, reveal_radius=1)
        self.visibility_state.initialize(self.goal, self.rows, self.cols)
        self.planner = POLevel4Planner(self.transition_model)

        self.current_belief = None
        self.expanded_nodes = 0
        self.execution_time = 0.0
        self.total_cost = 0
        self.fog_mode = tk.StringVar(value=MODE_1)
        self.animation_running = False
        self.animation_timer_id = None
        self.search_actions = []
        self.visited_positions = set()
        self.belief_history = []
        self.mode1_actions = []
        self.mode1_spawn = None

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

        self.control_frame = tk.Frame(self.main_frame, bg=self.PANEL, width=240)
        self.control_frame.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.control_frame.pack_propagate(False)

        tk.Label(
            self.control_frame,
            text="Complex Environment",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(20, 15))


        fog_menu = tk.OptionMenu(
            self.control_frame,
            self.fog_mode,
            MODE_1,
            MODE_AND_OR,
            MODE_3
        )
        fog_menu.config(
            bg="#40444B",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            width=20,
            relief="flat"
        )
        fog_menu.pack(pady=6)

        self.mode_hint = tk.Label(
            self.control_frame,
            text=self.mode_description(self.fog_mode.get()),
            bg=self.PANEL,
            fg="#D0D7E2",
            justify="left",
            wraplength=200,
            font=("Segoe UI", 9)
        )
        self.mode_hint.pack(padx=14, pady=(0, 10))

        self.fog_mode.trace_add("write", self._on_mode_change)


        self.run_btn = self.create_button("Run AI", self.run_ai)
        self.reset_btn = self.create_button("Reset", self.reset)
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

        self.fog_img = self.load_fog_image()
        self.steve_ghost_img = self.load_ghost_player_image()
        self.prepare_mode1_spawn()
        self.render_scene()

    def _on_mode_change(self, *_):
        if self.fog_mode.get() == MODE_1 and self.mode1_spawn is None:
            self.prepare_mode1_spawn()
        if self.fog_mode.get() == MODE_1 and self.mode1_spawn is not None:
            self.actual_position = self.mode1_spawn
        self.mode_hint.config(text=self.mode_description(self.fog_mode.get()))
        self.render_scene()

    def mode_description(self, mode):
        if mode == MODE_1:
            return (
                "Sensorless Search.\n"
                "Steve's exact location is unknown.\n"
                "The planner reasons over a belief state."
            )

        if mode == MODE_AND_OR:
            return (
                "AND-OR Search.\n"
                "The environment is fully observable.\n"
                "The planner handles branching outcomes."
            )

        return (
            "Partially Observable.\n"
            "The goal is hidden by fog and is gradually revealed\n"
            "through observations."
        )

    def _find_cell(self, value):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.world_grid[row][col] == value:
                    return (row, col)
        return None

    def load_fog_image(self):
        asset_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
        path = os.path.join(asset_dir, "fog.png")

        try:
            if os.path.exists(path):
                img = Image.open(path)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img = img.resize((64, 64))
                return ImageTk.PhotoImage(img)
        except Exception:
            pass

        img = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
        pixels = img.load()

        for y in range(64):
            for x in range(64):
                if (x + y) % 3 == 0:
                    pixels[x, y] = (255, 255, 255, 220)
                elif (x + y) % 5 == 0:
                    pixels[x, y] = (255, 255, 255, 200)

        for y in range(20, 44):
            for x in range(12, 52):
                if (x * y) % 17 == 0:
                    pixels[x, y] = (255, 255, 255, 245)

        try:
            img.save(path)
        except Exception:
            pass

        return ImageTk.PhotoImage(img)

    def load_ghost_player_image(self):
        asset_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
        path = os.path.join(asset_dir, "steve_job.png")

        try:
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA").resize((60, 60))
                alpha = img.getchannel("A")
                alpha = alpha.point(lambda value: int(value * 0.35))
                img.putalpha(alpha)
                return ImageTk.PhotoImage(img)
        except Exception:
            pass

        img = Image.new("RGBA", (60, 60), (255, 255, 255, 0))
        pixels = img.load()
        for y in range(12, 48):
            for x in range(18, 42):
                if (x + y) % 3 != 0:
                    pixels[x, y] = (255, 255, 255, 90)
        return ImageTk.PhotoImage(img)

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

    def reset(self):
        self.cancel_animation()
        self.world_grid = copy.deepcopy(self.original_world_grid)
        self.rows = len(self.world_grid)
        self.cols = len(self.world_grid[0])
        self.start = self._find_cell("S")
        self.goal = self._find_cell("D")
        self.actual_position = self.start
        self.visibility_state = POVisibilityState(fog_radius=2, reveal_radius=1)
        self.visibility_state.initialize(self.goal, self.rows, self.cols)
        self.current_belief = None
        self.expanded_nodes = 0
        self.execution_time = 0.0
        self.total_cost = 0
        self.search_actions = []
        self.visited_positions = set()
        self.belief_history = []
        self.mode1_actions = []
        self.mode1_spawn = None
        self.prepare_mode1_spawn()
        self.render_scene()
        self.info.config(text="Ready...")

    def back_to_menu(self):
        self.window.destroy()
        self.root.deiconify()

    def run_ai(self):
        self.info.config(text="Planning under partial observability...")
        self.window.update_idletasks()

        self.world_grid = copy.deepcopy(self.original_world_grid)
        self.rows = len(self.world_grid)
        self.cols = len(self.world_grid[0])
        self.start = self._find_cell("S")
        self.goal = self._find_cell("D")

        self.search_actions = []
        self.visited_positions = set()
        self.belief_history = []
        self.expanded_nodes = 0
        self.total_cost = 0
        self.execution_time = 0.0
        self.visibility_state = POVisibilityState(fog_radius=2, reveal_radius=1)
        self.visibility_state.initialize(self.goal, self.rows, self.cols)
        self.mode1_actions = []
        self.current_belief = self.initial_belief_for_mode()
        self.belief_history.append(POBeliefState(self.current_belief.positions, label=self.current_belief.label))

        if self.fog_mode.get() == MODE_1:
            if self.mode1_spawn is None:
                self.prepare_mode1_spawn()
            self.actual_position = self.mode1_spawn
            self.actual_position, self.mode1_actions, bfs_expanded = self.build_mode1_plan(self.mode1_spawn)
            self.expanded_nodes = bfs_expanded
        else:
            self.actual_position = self.start

        self.visited_positions = {self.actual_position}

        self.cancel_animation()
        self.animation_running = True
        self.render_scene()
        self._start_time = time.perf_counter()
        self._schedule_next_step()

    def move_cost(self, tile):
        if tile == 3:
            return 4
        if tile == 2:
            return 3
        if tile in (1, 1.5):
            return 2
        return 1

    def initial_belief_for_mode(self):
        mode = self.fog_mode.get()
        walkable_positions = self.get_walkable_positions()

        if mode == MODE_1:
            return POBeliefState(walkable_positions, label="steve")
        if mode == MODE_AND_OR:
            return POBeliefState([self.goal], label="goal")
        fog_candidates = self.visibility_state.active_mask()
        if not fog_candidates:
            fog_candidates = walkable_positions
        return POBeliefState(fog_candidates, label="goal")

    def _schedule_next_step(self):
        if not self.animation_running:
            return
        self.animation_timer_id = self.window.after(150, self._play_next_step)

    def cancel_animation(self):
        if self.animation_timer_id is not None:
            try:
                self.window.after_cancel(self.animation_timer_id)
            except Exception:
                pass
            self.animation_timer_id = None
        self.animation_running = False

    def _play_next_step(self):
        if not self.animation_running:
            return

        if self.actual_position == self.goal:
            self.execution_time = time.perf_counter() - self._start_time
            self.animation_running = False
            self.info.config(text=self.build_stats_text("Goal found"))
            self.render_scene()
            return

        if self.current_belief is not None and self.current_belief.belief_size() == 0:
            self.execution_time = time.perf_counter() - self._start_time
            self.animation_running = False
            self.info.config(text="No remaining belief states")
            return

        if self.fog_mode.get() == MODE_1:
            if not self.mode1_actions:
                self.execution_time = time.perf_counter() - self._start_time
                self.animation_running = False
                self.info.config(text="No Mode 1 plan found")
                return
            action = self.mode1_actions.pop(0)
        else:
            observation = self.observe_world()
            action, expanded = self.planner.next_action(
                observation,
                self.current_belief,
                self.goal,
                self.visited_positions
            )
            self.expanded_nodes += expanded

        if action is None:
            self.execution_time = time.perf_counter() - self._start_time
            self.animation_running = False
            self.info.config(text="No further action found")
            return

        self.search_actions.append(action)
        destination = self.transition_model.move(
            self.world_grid,
            self.actual_position,
            action
        )
        self.actual_position = destination
        original_tile = self.original_world_grid[self.actual_position[0]][self.actual_position[1]]
        self.total_cost += self.move_cost(original_tile)
        self._dig_trail(self.actual_position)
        self.visited_positions.add(self.actual_position)

        if self.fog_mode.get() == MODE_1:
            self.current_belief = POBeliefState(
                self.transition_model.propagate_belief(
                    self.world_grid,
                    self.current_belief.positions,
                    action
                ),
                label="steve"
            )
        else:
            self.visibility_state.reveal_from_position(self.actual_position)
            post_observation = self.observe_world()
            self.current_belief = self.update_goal_belief(
                self.current_belief,
                post_observation
            )

        self.belief_history.append(
            POBeliefState(self.current_belief.positions, label=self.current_belief.label)
        )
        self.render_scene()
        self.info.config(text=self.build_stats_text())
        self._schedule_next_step()

    def _dig_trail(self, position):
        row, col = position
        if self.world_grid[row][col] in (1, 1.5, 2, 3):
            self.world_grid[row][col] = 0

    def prepare_mode1_spawn(self):
        start_candidates = [
            (0, col)
            for col in range(self.cols)
            if self.transition_model.is_walkable(self.world_grid, (0, col))
        ]
        if not start_candidates:
            self.mode1_spawn = self.start
            if self.fog_mode.get() == MODE_1:
                self.actual_position = self.mode1_spawn
            return self.mode1_spawn

        self.mode1_spawn = random.choice(start_candidates)
        if self.fog_mode.get() == MODE_1:
            self.actual_position = self.mode1_spawn
        return self.mode1_spawn

    def build_mode1_plan(self, spawn):
        if spawn is None:
            return self.start, [], 0

        left_actions = ["left"] * 12
        corner_position = spawn
        for action in left_actions:
            corner_position = self.transition_model.move(self.world_grid, corner_position, action)

        bfs_actions, expanded = self.find_bfs_actions(corner_position, self.goal)
        if bfs_actions is None:
            return spawn, left_actions, expanded

        return spawn, left_actions + bfs_actions, expanded

    def find_bfs_actions(self, start, goal):
        queue = deque([start])
        parents = {start: None}
        actions = ["up", "down", "left", "right"]
        expanded = 0

        while queue:
            current = queue.popleft()
            expanded += 1
            if current == goal:
                break

            for action in actions:
                nxt = self.transition_model.move(self.world_grid, current, action)
                if nxt in parents:
                    continue
                parents[nxt] = (current, action)
                queue.append(nxt)

        if goal not in parents:
            return None, expanded

        path_actions = []
        current = goal
        while current != start:
            parent, action = parents[current]
            path_actions.append(action)
            current = parent
        path_actions.reverse()
        return path_actions, expanded

    def observe_world(self):
        world_state = POWorldState(
            grid=self.world_grid,
            actual_position=self.actual_position,
            goal_position=self.goal,
            start_position=self.start
        )
        return self.observation_model.observe(
            world_state,
            self.fog_mode.get(),
            self.visibility_state
        )

    def update_goal_belief(self, belief, observation):
        updated = set(belief.positions)
        if observation.mode == MODE_AND_OR:
            return POBeliefState({self.goal}, label="goal")

        if observation.mode == MODE_3:
            updated -= self.visibility_state.revealed

        if observation.goal_position is not None:
            updated = {self.goal}

        return POBeliefState(updated, label="goal")

    def build_stats_text(self, prefix=None):
        mode = self.fog_mode.get()
        planner_label = "AND-OR Search" if mode == MODE_AND_OR else "Mode-aware Planner"
        belief_size = self.current_belief.belief_size() if self.current_belief else 0

        lines = []
        if prefix:
            lines.append(prefix)
            lines.append("")
        lines.extend([
            f"Algorithm : {planner_label}",
            "",
            f"Mode           : {mode}",
            f"Expanded Nodes : {self.expanded_nodes}",
            f"Time : {self.execution_time:.6f}s",
            f"Total Cost     : {self.total_cost}",
        ])
        if mode != MODE_1:
            lines.append(f"Goal Belief    : {belief_size}")
        return "\n".join(lines)

    def get_walkable_positions(self):
        positions = []
        for row in range(self.rows):
            for col in range(self.cols):
                if self.world_grid[row][col] != 4:
                    positions.append((row, col))
        return positions

    def render_scene(self):
        observation = self.observe_world()
        self.renderer.draw_map(observation.grid)

        if self.fog_mode.get() == MODE_1:
            self.draw_player(ghost=True)
        elif self.fog_mode.get() == MODE_3:
            self.draw_fog(observation.fog_mask)
            self.draw_player()
        else:
            self.draw_player()

    def draw_player(self, ghost=False):
        self.canvas.delete("steve")
        if ghost or self.fog_mode.get() == MODE_1:
            image = self.steve_ghost_img
        else:
            image = self.renderer.steve_img

        self.canvas.create_image(
            self.actual_position[1] * 64,
            self.actual_position[0] * 64,
            image=image,
            anchor="nw",
            tags="steve"
        )

    def draw_fog(self, fog_mask):
        self.canvas.delete("fog")
        for row, col in fog_mask:
            self.canvas.create_image(
                col * 64,
                row * 64,
                image=self.fog_img,
                anchor="nw",
                tags="fog"
            )

    def on_close(self):
        self.cancel_animation()
        self.window.destroy()
        self.root.deiconify()
