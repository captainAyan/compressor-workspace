import tkinter as tk

from utility import center_dialog 

def show_info_dialog(parent, title_text, content_text):
    """Creates a custom modal popup dialog for Help or Shortcuts."""
    dialog = tk.Toplevel(parent)
    dialog.title(title_text)
    dialog.geometry("350x250")
    dialog.transient(parent)
    dialog.grab_set()

    label = tk.Label(dialog, text=content_text, justify="left", padx=20, pady=20, font=("Arial", 10))
    label.pack(fill="both", expand=True)

    close_btn = tk.Button(dialog, text="Close", width=10, command=dialog.destroy)
    close_btn.pack(pady=10)

    center_dialog(parent, dialog)
