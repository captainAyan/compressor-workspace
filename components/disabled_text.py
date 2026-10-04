import tkinter as tk

class DisabledText(tk.Text):
    def __init__(self, master=None, **kwargs):
        defaults = {
            "height": 2,
            "width": 40,
            "wrap": tk.WORD,
            "bg": "#f4f4f4",
            "relief": tk.FLAT
        }
        defaults.update(kwargs)
        
        super().__init__(master, **defaults)
        self.config(state=tk.DISABLED)

    def set_text(self, text):
        self.config(state=tk.NORMAL)
        self.delete("1.0", tk.END)
        self.insert(tk.END, text)
        self.config(state=tk.DISABLED)
