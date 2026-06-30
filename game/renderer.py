# game/renderer.py

import tkinter as tk
import os
from PIL import Image, ImageTk
TILE_SIZE = 64


class Renderer:

    def __init__(self, canvas):

        self.canvas = canvas

        asset_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "images"
        )
        self.grass_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "grass.jpg")
            ).resize((64, 64))
        )        
        self.dirt_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "dirt.jpg")
            ).resize((64, 64))
        )

        self.stone_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "stone.jpg")
            ).resize((64, 64))
        )

        self.obsidian_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "obsidian.jpg")
            ).resize((64, 64))
        )

        self.diamond_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "diamond.jpg")
            ).resize((64, 64))
        )

        self.steve_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "steve_job.png")
            ).resize((60, 60))
        )
        self.bedrock_img    = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "bedrock.png")
            ).resize((64, 64))
        )
        self.background_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "background.png")
            ).resize((768, 768))
        )
        self.background_dirt_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "background_dirt.png")
            ).resize((768, 640))
        )
        self.zombie_img = ImageTk.PhotoImage(
            Image.open(
                os.path.join(asset_dir, "zombie.jpg")
            ).resize((60,60))
        ) 
    def draw_map(self, grid):

        self.canvas.delete("all")
        # Background
        self.canvas.create_image(
            0,
            0,
            image=self.background_img,
            anchor="nw"
        )
        self.canvas.create_image(
            0,
            64,
            image=self.background_dirt_img,
            anchor="nw"
        )
        for r in range(len(grid)):
            for c in range(len(grid[0])):

                x = c * TILE_SIZE
                y = r * TILE_SIZE

                value = grid[r][c]

                if value == 1:
                    self.canvas.create_image(
                        x,
                        y,
                        image=self.dirt_img,
                        anchor="nw"
                    )
                elif value == 1.5:
                    self.canvas.create_image(
                        x,
                        y,
                        image=self.grass_img,
                        anchor="nw"
                    )
                elif value == 4:
                    self.canvas.create_image(
                        x,
                        y,
                        image=self.bedrock_img,
                        anchor="nw"
                    )
                elif value == 2:
                    self.canvas.create_image(
                        x,
                        y,
                        image=self.stone_img,
                        anchor="nw"
                    )

                elif value == 3:
                    self.canvas.create_image(
                        x,
                        y,
                        image=self.obsidian_img,
                        anchor="nw"
                    )

                elif value == "D":
                    self.canvas.create_image(
                        x,
                        y,
                        image=self.diamond_img,
                        anchor="nw"
                    )


    def draw_path(self, path):

        for r, c in path:

            x1 = c * TILE_SIZE + 16
            y1 = r * TILE_SIZE + 16

            x2 = x1 + 32
            y2 = y1 + 32

            self.canvas.create_oval(
                x1,
                y1,
                x2,
                y2,
                fill="blue"
            )

            self.canvas.update()
    def animate_path(self, path):

        steve = None

        for r, c in path:

            if steve:
                self.canvas.delete(steve)

            x = c * TILE_SIZE + 8
            y = r * TILE_SIZE + 8

            steve = self.canvas.create_image(
                x,
                y,
                image=self.steve_img,
                anchor="nw"
            )

            self.canvas.update()

            self.canvas.after(150)