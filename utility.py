import tkinter as tk

def disabled_text_view_updater(text_view, text):
    text_view.config(state=tk.NORMAL)
    text_view.delete("1.0", tk.END)
    text_view.insert(tk.END, text)
    text_view.config(state=tk.DISABLED)


