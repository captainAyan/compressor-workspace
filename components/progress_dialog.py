import threading
import time
import tkinter as tk
from tkinter import ttk


class ProgressDialog:
    def __init__(self, parent, title="Please Wait", message="Processing..."):
        self.parent = parent
        self.default_title = title
        self.default_message = message
        self.top = None
        self.progress = None
        self.label = None

    def show(self, message=None, title=None):
        if self.top is not None:
            return  # Already open, ignore duplicate calls

        t = title if title else self.default_title
        m = message if message else self.default_message

        self.top = tk.Toplevel(self.parent)
        self.top.title(t)
        self.top.geometry("300x120")
        self.top.resizable(False, False)

        # Modal configuration & block manual close
        self.top.transient(self.parent)
        self.top.grab_set()
        self.top.protocol("WM_DELETE_WINDOW", lambda: None)

        # Widgets
        self.label = ttk.Label(self.top, text=m, wraplength=260)
        self.label.pack(pady=(20, 10))

        self.progress = ttk.Progressbar(
            self.top, orient="horizontal", length=250, mode="indeterminate"
        )
        self.progress.pack(pady=10)

        self.progress.start(10)
        self.center_window()

    def close(self):
        if self.top is not None:
            try:
                self.progress.stop()
                self.top.grab_release()
                self.top.destroy()
            except Exception:
                pass
            finally:
                self.top = None
                self.progress = None
                self.label = None

    def center_window(self):
        self.top.update_idletasks()
        p_x = self.parent.winfo_rootx()
        p_y = self.parent.winfo_rooty()
        p_w = self.parent.winfo_width()
        p_h = self.parent.winfo_height()

        d_w = self.top.winfo_width()
        d_h = self.top.winfo_height()

        x = p_x + (p_w - d_w) // 2
        y = p_y + (p_h - d_h) // 2
        self.top.geometry(f"+{x}+{y}")

