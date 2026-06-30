import tkinter as tk

from game.menu import MainMenu


def main():

    root = tk.Tk()

    root.title("Treasure Mining AI")

    root.geometry("1000x700")

    root.resizable(False, False)

    MainMenu(root)

    root.mainloop()


if __name__ == "__main__":
    main()
    