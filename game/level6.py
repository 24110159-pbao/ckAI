import copy
import tkinter as tk
import random

from game.maps import Maps
from game.renderer import Renderer

from algorithms.adversarial.minimax import Minimax
from algorithms.adversarial.alphabeta import AlphaBeta
from algorithms.adversarial.expectimax import Expectimax
import time

# ======================================================
# GAME STATE
# ======================================================

class GameState:

    def __init__(self, grid, steve, zombie, diamond):
        
        self.grid = grid
        self.steve = steve
        self.zombie = zombie
        self.diamond = diamond

    def copy(self):
        return GameState(
            copy.deepcopy(self.grid),
            tuple(self.steve),
            tuple(self.zombie),
            tuple(self.diamond)
        )

    def move_steve(self, move):

        self.steve = move

    def move_zombie(self, move):
        self.zombie = move

    def evaluate(self):
        if self.steve == self.zombie:
            return -100000
        
        if self.steve == self.diamond:
            return 100000

        

        sr, sc = self.steve
        zr, zc = self.zombie
        dr, dc = self.diamond

        dist_diamond = abs(dr-sr) + abs(dc-sc)
        dist_zombie = abs(zr-sr) + abs(zc-sc)

        score = 0

        # càng gần diamond càng tốt
        score -= dist_diamond * 8

        # càng xa zombie càng tốt
        score += dist_zombie * 5

        return score
    
    def is_terminal(self):
        return (
            self.steve == self.zombie
            or self.steve == self.diamond
        )

    def get_steve_moves(self):
        return self.__moves(self.steve)

    def get_zombie_moves(self):
        return self.__moves(self.zombie)

    def __moves(self, pos):

        r, c = pos
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]

        moves = []

        for dr, dc in dirs:

            nr, nc = r + dr, c + dc

            if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]):

                if self.grid[nr][nc] != 4:
                    moves.append((nr, nc))

        return moves


# ======================================================
# LEVEL 6
# ======================================================

class Level6:

    def __init__(self, root):

        self.root = root

        self.execution_time = 0

        self.window = tk.Toplevel(root)
        self.window.title("Level 6 - Adversarial Search")

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

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid = Maps.get_level(6)

        self.steve = (0, 0)

        self.zombie = next(
            (r,c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "Z"
        )

        self.goal = next(
            (r,c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "D"
        )

        self.running = False
        self.turn = 0          # Đếm số lượt
        self.MAX_TURN = 30      # Sau 40 lượt thì hòa
        self.BG = "#202225"
        self.PANEL = "#2F3136"
        self.BUTTON = "#5865F2"
        self.BUTTON_HOVER = "#4752C4"
        self.TEXT = "white"

        self.window.configure(bg=self.BG)

        self.main_frame = tk.Frame(self.window, bg=self.BG)
        self.main_frame.pack(fill="both", expand=True)

        rows = len(self.grid)
        cols = len(self.grid[0])

        self.canvas = tk.Canvas(
            self.main_frame,
            width=cols * 64,
            height=rows * 64,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side="left", padx=10, pady=10)

        self.renderer = Renderer(self.canvas)

        self.control = tk.Frame(
            self.main_frame,
            bg=self.PANEL,
            width=220
        )

        self.control.pack(
            side="right",
            fill="y",
            padx=(0,10),
            pady=10
        )

        self.control.pack_propagate(False)

        tk.Label(
            self.control,
            text="AI Controls",
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Segoe UI",16,"bold")
        ).pack(pady=(20,15))

        self.algorithm = tk.StringVar(value="Minimax")

        algo_menu = tk.OptionMenu(
            self.control,
            self.algorithm,
            "Minimax",
            "Alpha-Beta",
            "Expectimax"
        )

        algo_menu.config(
            bg="#40444B",
            fg="white",
            font=("Segoe UI",11,"bold"),
            width=10,
            relief="flat"
        )

        algo_menu.pack(pady=10)

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

        stats_frame = tk.LabelFrame(
            self.control,
            text="Statistics",
            bg=self.PANEL,
            fg=self.TEXT,
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
            font=("Consolas",10)
        )

        self.info.pack(
            padx=10,
            pady=10
        )

        self.renderer.draw_map(self.grid)
        self.draw_players()

    # ==================================================

    def draw_players(self):

        self.canvas.delete("p")

        sr, sc = self.steve
        zr, zc = self.zombie

        self.canvas.create_image(
            sc * 64,
            sr * 64,
            image=self.renderer.steve_img,
            anchor="nw",
            tags="p"
        )

        self.canvas.create_image(
            zc * 64,
            zr * 64,
            image=self.renderer.zombie_img,
            anchor="nw",
            tags="p"
        )

    # ==================================================
    def run_ai(self):


        if self.running:
            return

        # Chỉ reset vị trí nhân vật
        self.steve = (0, 0)
        self.turn = 0

        self.zombie = next(
            (r, c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "Z"
        )

        self.renderer.draw_map(self.grid)
        self.draw_players()

        self.running = True
        self.set_buttons_state("disabled")
        self.update_info()
        self.execution_time = 0
        self.step()
    # ==================================================

    def step(self):

        if not self.running:
            return
        self.turn += 1
        self.update_info()
        if self.turn >= self.MAX_TURN:

            self.renderer.draw_map(self.grid)
            self.draw_players()

            self.update_info("DRAW")
            self.running = False
            self.set_buttons_state("normal")
            return
        # ======================
        # STATE HIỆN TẠI
        # ======================

        state = GameState(
            self.grid,
            self.steve,
            self.zombie,
            self.goal
        )

        algo = self.algorithm.get()

        # ======================
        # STEVE
        # ======================
        t0 = time.perf_counter()

        if algo == "Minimax":
            _, move, _ = Minimax.search(state, 2, True)

        elif algo == "Alpha-Beta":
            _, move, _ = AlphaBeta.search(state, 2, True)

        else:
            _, move, _ = Expectimax.search(state, 2, True)

        self.execution_time += time.perf_counter() - t0

        if move:
            new_r, new_c = move

            if self.grid[new_r][new_c] in (1, 1.5):
                self.grid[new_r][new_c] = 0

            self.steve = move

        # Steve tới Diamond
        if self.steve == self.goal:

            self.renderer.draw_map(self.grid)
            self.draw_players()


            self.update_info("STEVE WIN")
            self.running = False
            self.set_buttons_state("normal")
            return

        # ======================
        # STATE MỚI
        # ======================

        state = GameState(
            self.grid,
            self.steve,
            self.zombie,
            self.goal
        )

        # ======================
        # ZOMBIE
        # ======================

        moves = state.get_zombie_moves()

        if moves:

            if algo == "Expectimax":
                move = random.choice(moves)

                new_r, new_c = move

                if self.grid[new_r][new_c] in (1, 1.5):
                    self.grid[new_r][new_c] = 0

                self.zombie = move

            else:

                best_score = float("inf")
                best_move = None

                for m in moves:

                    child = state.copy()
                    child.move_zombie(m)

                    score, _, _ = AlphaBeta.search(child, 2, False)

                    if score < best_score:

                        best_score = score
                        best_move = m

                if best_move:
                    new_r, new_c = best_move

                    if self.grid[new_r][new_c] in (1, 1.5):
                        self.grid[new_r][new_c] = 0

                    self.zombie = best_move

        # ======================
        # DRAW
        # ======================

        self.renderer.draw_map(self.grid)
        self.draw_players()

        # Zombie bắt Steve

        if self.zombie == self.steve:


            self.update_info("ZOMBIE WIN")
            self.running = False
            self.set_buttons_state("normal")
            return

        self.window.after(300, self.step)

    # ==================================================

    def reset(self):
        self.grid = Maps.get_level(6)
        self.steve = (0,0)

        self.zombie = next(
            (r,c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "Z"
        )

        self.goal = next(
            (r,c)
            for r in range(len(self.grid))
            for c in range(len(self.grid[0]))
            if self.grid[r][c] == "D"
        )

        self.renderer.draw_map(self.grid)
        self.draw_players()

        self.running = False
        self.set_buttons_state("normal")
        self.turn = 0          # Đếm số lượt
        self.MAX_TURN = 30      # Sau 40 lượt thì hòa
        self.update_info("Ready")

    def on_close(self):
        self.window.destroy()
        self.root.deiconify()

    def create_button(self, text, command):

        btn = tk.Button(
            self.control,
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
        self.running = False
        self.window.destroy()
        self.root.deiconify()

    def update_info(self, status="Running"):

        avg_time = self.execution_time / self.turn if self.turn else 0

        self.info.config(
            text=
            f"Algorithm : {self.algorithm.get()}\n\n"
            f"Turn    : {self.turn}\n"
            f"Time  : {avg_time:.5f} s/turn\n"
            f"Status : {status}"
        )