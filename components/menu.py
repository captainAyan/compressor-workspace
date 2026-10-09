import tkinter as tk

class Menubar:
    def __init__(self, parent, callbacks: dict):
        self.parent = parent
        self.callbacks = callbacks
        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self.parent)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Files", accelerator="Ctrl+Shift+F", command=self.callbacks.get("select_files"))
        file_menu.add_command(label="Select Folder", accelerator="Ctrl+F", command=self.callbacks.get("select_folder"))
        file_menu.add_command(label="Select Destination", accelerator="Ctrl+D", command=self.callbacks.get("select_destination"))
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.callbacks.get("save"))
        file_menu.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self.callbacks.get("save_as"))
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.parent.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Swap View", accelerator="Alt+S", command=self.callbacks.get("swap_view"))
        view_menu.add_command(label="View Heatmap", accelerator="Alt+H", command=self.callbacks.get("toggle_heatmap"))
        view_menu.add_separator()
        view_menu.add_command(label="Reset View", accelerator="Ctrl+R", command=self.callbacks.get("reset_view"))
        menubar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.callbacks.get("about_view_action"))
        help_menu.add_command(label="Shortcuts", command=self.callbacks.get("shortcuts_view_action"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.parent.config(menu=menubar)
