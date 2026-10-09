import tkinter as tk
from tkinter import ttk

from strings import GREEN_COLOUR, RED_COLOUR, YELLOW_COLOUR


class Statusbar():
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    DEFAULT = "default"

    def __init__(self, root):
        self.root = root

        self.create_widget()

    def create_widget(self):
        self.bottom_stats_label = ttk.Label(
            self.root, text="", font=("Arial", 9))
        self.bottom_stats_label.pack(fill=tk.X, expand=True, side=tk.LEFT)

    def set_status(self, text, type):
        if type == Statusbar.SUCCESS:
            background = GREEN_COLOUR
            foreground = "white"
        elif type == Statusbar.ERROR:
            background = RED_COLOUR
            foreground = "white"
        elif type == Statusbar.WARNING:
            background = YELLOW_COLOUR
            foreground = "white"
        elif type == Statusbar.DEFAULT:
            background="SystemButtonFace"
            foreground="SystemButtonText"

        self.bottom_stats_label.config(text=text, background=background, foreground=foreground)

