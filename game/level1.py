import tkinter as tk
import time

from game.maps import Maps
from game.renderer import Renderer

from algorithms.uninformed.bfs import BFS
from algorithms.uninformed.dfs import DFS
from algorithms.uninformed.ids import IDS
import copy

class Level1:

    def __init__(self, root):
        self.original_grid = copy.deepcopy(Maps.get_level(1))
        self.grid = copy.deepcopy(self.original_grid)
        self.root = root

        self.window = tk.Toplevel(root)
        self.window.title("Level 1 - BFS DFS IDS")

        # ================= WINDOW =================
        window_width = 1050
        window_height = 820

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        self.window.geometry(
            f"{window_width}x{window_height}+{x}+{y}"
        )

        self.window.resizable(False, False)
        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        # ================= DATA =================

        self.start = (0, 0)
        self.running = False
        self.goal = next(
            (r, c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "D"
)

        # ================= COLORS =================
        self.BG = "#202225"
        self.PANEL = "#2F3136"
        self.BUTTON = "#5865F2"
        self.BUTTON_HOVER = "#4752C4"
        self.TEXT = "white"

        self.window.configure(bg=self.BG)

        # ================= MAIN LAYOUT =================
        self.main_frame = tk.Frame(
            self.window,
            bg=self.BG
        )
        self.main_frame.pack(
            fill="both",
            expand=True
        )

        # ================= MAP =================
        rows = len(self.grid)
        cols = len(self.grid[0])
        self.canvas = tk.Canvas(
            self.main_frame,
            width=cols * 64,
            height=rows * 64,
            highlightthickness=0,
            bd=0
        )

        self.canvas.pack(
            side="left",
            padx=10,
            pady=10
        )

        self.renderer = Renderer(self.canvas)

        # ================= CONTROL PANEL =================
        self.control_frame = tk.Frame(
            self.main_frame,
            bg=self.PANEL,
            width=220
        )

        self.control_frame.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10
        )

        self.control_frame.pack_propagate(False)

        # ================= TITLE =================
        tk.Label(
            self.control_frame,
            text="AI Controls",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(20, 15))

        # ================= ALGORITHM =================
        self.algorithm = tk.StringVar(value="BFS")

        algo_menu = tk.OptionMenu(
            self.control_frame,
            self.algorithm,
            "BFS",
            "DFS",
            "IDS"
        )

        algo_menu.config(
            bg="#40444B",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            width=10,
            relief="flat"
        )

        algo_menu.pack(pady=10)

        # ================= BUTTONS =================
        self.run_btn = self.create_button(
            "Run AI",
            self.run_ai
        )

        self.reset_btn = self.create_button(
            "Reset",
            self.reset
        )

        self.create_button(
            "Back To Menu",
            self.back_to_menu
        )

        # ================= STATS =================
        stats_frame = tk.LabelFrame(
            self.control_frame,
            text="Statistics",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI", 10, "bold")
        )

        stats_frame.pack(
            fill="x",
            padx=10,
            pady=20
        )

        self.info = tk.Label(
            stats_frame,
            text="Ready...",
            bg=self.PANEL,
            fg="white",
            justify="left",
            font=("Consolas", 10)
        )

        self.info.pack(
            padx=10,
            pady=10
        )

        # ================= DRAW MAP =================
        self.renderer.draw_map(self.grid)

    # ==========================================
    # BUTTON FACTORY
    # ==========================================
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
    # ==========================================
    # ENABLE / DISABLE BUTTON
    # ==========================================
    def set_buttons_state(self, state):

        self.run_btn.config(state=state)
        self.reset_btn.config(state=state)

    # ==========================================
    # RESET
    # ==========================================
    def reset(self):

        self.grid = copy.deepcopy(self.original_grid)

        self.goal = next(
            (r, c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "D"
        )

        self.renderer.draw_map(self.grid)

        self.info.config(
            text="Ready..."
        )

    # ==========================================
    # BACK MENU
    # ==========================================
    def back_to_menu(self):

        self.window.destroy()
        self.root.deiconify()

    # ==========================================
    # RUN AI
    # ==========================================
    def run_ai(self):
        if self.running:
            return
        self.grid = copy.deepcopy(self.original_grid)
        self.renderer.draw_map(self.grid)
        self.running = True
        self.set_buttons_state("disabled")
        algo = self.algorithm.get()

        start_time = time.perf_counter()

        if algo == "BFS":
            path, expanded = BFS.search(
                self.grid,
                self.start,
                self.goal
            )

        elif algo == "DFS":
            path, expanded = DFS.search(
                self.grid,
                self.start,
                self.goal
            )

        else:
            path, expanded = IDS.search(
                self.grid,
                self.start,
                self.goal
            )

        end_time = time.perf_counter()

        if path is None:

            self.info.config(
                text="No path found"
            )

            self.running = False
            self.set_buttons_state("normal")

            return
        
        cost = self.calculate_cost(path)
        self.animate_steve(path)

        

        self.info.config(
            text=
            f"Algorithm : {algo}\n\n"
            f"Expanded  : {expanded}\n"
            f"Total Cost      : {cost}\n"
            f"Time      : {end_time - start_time:.6f}s"
        )
        self.running = False
        self.set_buttons_state("normal")

    # ==========================================
    # ANIMATION
    # ==========================================
    def animate_steve(self, path):

        for r, c in path:

            if self.grid[r][c] == 1 or self.grid[r][c] == 1.5:
                self.grid[r][c] = 0

            self.renderer.draw_map(
                self.grid
            )

            self.canvas.delete("steve")

            self.canvas.create_image(
                c * 64,
                r * 64,
                image=self.renderer.steve_img,
                anchor="nw",
                tags="steve"
            )

            self.canvas.update()
            self.canvas.after(150)

    # ==========================================
    # CLOSE
    # ==========================================
    def on_close(self):

        self.window.destroy()
        self.root.deiconify()
    def calculate_cost(self, path):
        cost = 0

        for r, c in path[1:]:  # Bỏ ô xuất phát
            if self.grid[r][c] in (1, 1.5):
                cost += 2
            else:
                cost += 1

        return cost

