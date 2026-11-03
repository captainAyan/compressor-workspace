import tkinter as tk
from tkinter import messagebox, ttk

from components.session_data_view import SessionDataView
from utility import center_dialog


class SessionDataExporterDialog(tk.Toplevel):
    def __init__(self, parent, session_data, on_save):
        super().__init__(parent)
        self.title("Export Session Data")
        self.geometry("800x520")
        self.minsize(800, 520)

        self.transient(parent)
        self.grab_set()

        center_dialog(parent, self)

        self.on_save_cb = on_save

        compressed_file_list_group = tk.Frame(self, padx=10, pady=10)
        compressed_file_list_group.pack(fill=tk.BOTH, expand=True)
        self.session_data_view = SessionDataView(compressed_file_list_group)
        self.session_data_view.refresh(session_data)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.on_cancel, width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

        save_btn = ttk.Button(button_frame, text="Save", command=self.on_save, width=10)
        save_btn.pack(side=tk.RIGHT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_save(self):
        self.on_save_cb()
        self.destroy()

    def on_cancel(self):
        self.destroy()
