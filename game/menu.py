import tkinter as tk
from PIL import Image, ImageTk
import os


class MainMenu:

    def __init__(self, root):
        self.root = root

        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        # =========================
        # BACKGROUND IMAGE
        # =========================
        img_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "images",
            "menu.jpg"
        )

        img = Image.open(img_path)
        img = img.resize((1000, 700))
        self.bg = ImageTk.PhotoImage(img)

        tk.Label(
            self.frame,
            image=self.bg
        ).place(x=0, y=0, relwidth=1, relheight=1)

        # =========================
        # PANEL (MENU BOX)
        # =========================
        self.panel = tk.Frame(
            self.frame,
            bg="#2b2b2b",
            bd=5,
            relief="ridge"
        )

        self.panel.place(
            relx=0.5,
            rely=0.55,
            anchor="center",
            width=420,
            height=500
        )

        # =========================
        # TITLE
        # =========================
        tk.Label(
            self.frame,
            text="⛏ TREASURE MINING AI ⛏",
            font=("Arial", 24, "bold"),
            fg="#FFD700",
            bg="#2b2b2b"
        ).place(
            relx=0.5,
            y=140,
            anchor="center"
        )

        # =========================
        # BUTTONS
        # =========================
        levels = [
            ("Level 1 - uninformed search", self.level1),
            ("Level 2 - informed search", self.level2),
            ("Level 3 - local search", self.level3),
            ("Level 4 - complex problems", self.level4),
            ("Level 5 - csp", self.level5),
            ("Level 6 - adversarial search", self.level6),
        ]

        y = 60
        for text, cmd in levels:
            self.create_button(text, cmd, y)
            y += 55

        # EXIT BUTTON
        tk.Button(
            self.panel,
            text="EXIT",
            command=self.root.destroy,
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg="#d32f2f",
            fg="white",
            cursor="hand2"
        ).place(
            relx=0.5,
            y=390,
            anchor="center"
        )


    # =========================
    # BUTTON FACTORY
    # =========================
    def create_button(self, text, command, y):
        tk.Button(
            self.panel,
            text=text,
            command=command,
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            cursor="hand2",
            relief="raised",
            bd=3
        ).place(
            relx=0.5,
            y=y,
            anchor="center"
        )

    # =========================
    # LEVEL SWITCHING
    # =========================
    def open_level(self, level_class):
        self.root.withdraw() 
        level_class(self.root)

    def level1(self):
        from game.level1 import Level1
        self.open_level(Level1)

    def level2(self):
        from game.level2 import Level2
        self.open_level(Level2)

    def level3(self):
        from game.level3 import Level3
        self.open_level(Level3)

    def level4(self):
        from game.level4 import Level4
        self.open_level(Level4)

    def level5(self):
        from game.level5 import Level5
        self.open_level(Level5)

    def level6(self):
        from game.level6 import Level6
        self.open_level(Level6)