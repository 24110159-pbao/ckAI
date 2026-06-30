import tkinter as tk
import time

from game.maps import Maps
from game.renderer import Renderer

from algorithms.local.HillClimbing import HillClimbing
from algorithms.local.LocalBeamSearch import LocalBeamSearch
from algorithms.local.SimulatedAnnealing import SimulatedAnnealing
import copy

class Level3:

    def __init__(self, root):

        self.original_grid = copy.deepcopy(Maps.get_level(3))
        self.grid = copy.deepcopy(self.original_grid)

        self.root = root
        self.window = tk.Toplevel(root)
        self.window.title("Level 3 - Local Search")
        
        window_width = 1050
        window_height = 820

        x = (self.window.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.window.winfo_screenheight() // 2) - (window_height // 2)

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)



        self.start = next(
            (r, c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "S"
        )

        self.goal = next(
            (r, c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "D"
        )

        self.running = False

        # ================= UI =================

        # ================= COLORS =================
        self.BG = "#202225"
        self.PANEL = "#2F3136"
        self.BUTTON = "#5865F2"
        self.BUTTON_HOVER = "#4752C4"
        self.TEXT = "white"

        self.window.configure(bg=self.BG)

        # ================= MAIN =================
        self.main_frame = tk.Frame(
            self.window,
            bg=self.BG
        )
        self.main_frame.pack(fill="both", expand=True)

        rows = len(self.grid)
        cols = len(self.grid[0])

        # ================= MAP =================
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

        # ================= CONTROL =================
        self.control_frame = tk.Frame(
            self.main_frame,
            bg=self.PANEL,
            width=350
        )

        self.control_frame.pack(
            side="right",
            fill="y",
            padx=(0,10),
            pady=10
        )

        self.control_frame.pack_propagate(False)

        # ================= TITLE =================
        tk.Label(
            self.control_frame,
            text="Local Search",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI",16,"bold")
        ).pack(pady=(20,15))

        # ================= ALGORITHM =================
        self.algo = tk.StringVar(value="Hill Climbing")

        menu = tk.OptionMenu(
            self.control_frame,
            self.algo,
            "Hill Climbing",
            "Local Beam",
            "Sim Annealing"
        )

        menu.config(
            bg="#40444B",
            fg="white",
            width=15,
            relief="flat",
            font=("Segoe UI",11,"bold")
        )

        menu.pack(pady=10)

        # ================= BUTTONS =================
        self.run_btn = self.create_button(
            "Run AI",
            self.run
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
            fg="white",
            font=("Segoe UI",10,"bold")
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
            anchor="w",
            width=28,
            font=("Consolas",10)
        )

        self.info.pack(
            padx=10,
            pady=10
        )

        self.renderer.draw_map(self.grid)

    def create_button(self, text, cmd):
        tk.Button(
            self.control,
            text=text,
            command=cmd,
            bg=self.BUTTON,
            fg="white",
            width=18
        ).pack(pady=5)

    def run(self):

        if self.running:
            return
        
        self.grid = copy.deepcopy(self.original_grid)
        self.renderer.draw_map(self.grid)

        self.running = True
        self.set_buttons_state("disabled")

        algo = self.algo.get()

        start_time = time.perf_counter()

        if algo == "Hill Climbing":
            path, expanded, found = HillClimbing.search(
                self.grid,
                self.start,
                self.goal
            )

        elif algo == "Local Beam":
            path, expanded, found = LocalBeamSearch.search(
                self.grid,
                self.start,
                self.goal
            )

        else:
            path, expanded, found= SimulatedAnnealing.search(
                self.grid,
                self.start,
                self.goal
            )

        end_time = time.perf_counter()

        cost = self.calc_cost(path)
        if path:
            self.animate(path)

        if found:
            status = "Goal found"
        else:
            status = "No path (stuck)"

        self.info.config(
            text=
            f"Algorithm : {algo}\n\n"
            f"Status    : {status}\n"
            f"Expanded  : {expanded}\n"
            f"Total Cost      : {cost}\n"
            f"Time      : {end_time-start_time:.6f}s"
        )

        self.running = False
        self.set_buttons_state("normal")

    def calc_cost(self, path):

        if not path:
            return 0

        total = 0

        for r, c in path[1:]:
            total += self.move_cost(self.grid[r][c])

        return total

    def move_cost(self, value):

        if value == 3:
            return 4

        if value == 2:
            return 3

        if value in (1, 1.5):
            return 2

        return 1

    def animate(self, path):

        for r, c in path:
            # Xóa block sau khi Steve đi qua
            if self.grid[r][c] in (1, 1.5):
                self.grid[r][c] = 0

            # Nếu Level 3 có thêm loại block 2 và 3 cũng muốn biến mất
            elif self.grid[r][c] in (2, 3):
                self.grid[r][c] = 0

            self.renderer.draw_map(self.grid)

            self.canvas.delete("steve")

            self.canvas.create_image(
                c * 64,
                r * 64,
                image=self.renderer.steve_img,
                anchor="nw",
                tags="steve"
            )

            self.canvas.update()
            self.canvas.after(120)

    def reset(self):

        self.grid = copy.deepcopy(self.original_grid)

        self.start = next(
            (r, c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "S"
        )

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

    def on_close(self):

        self.window.destroy()
        self.root.deiconify()

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
            font=("Segoe UI",10,"bold")
        )

        btn.pack(pady=8)

        return btn
    
    def set_buttons_state(self, state):

        self.run_btn.config(state=state)
        self.reset_btn.config(state=state)

    def back_to_menu(self):

        self.window.destroy()
        self.root.deiconify()