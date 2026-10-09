import tkinter as tk
from tkinter import ttk


class CompressionController():
    def __init__(self, parent, on_try_cb, on_save_cb, on_save_as_cb):
        self.parent = parent
        self.on_try_cb = on_try_cb
        self.on_save_cb = on_save_cb
        self.on_save_as_cb = on_save_as_cb

        self.create_widget()

    def get_compression_parameters(self):
        quality = int(self.quality_cb.get())
        img_format = self.format_cb.get()
        optimize = self.optimize_var.get()

        return quality, img_format, optimize

    def create_widget(self):
        q_row = ttk.Frame(self.parent)
        q_row.pack(fill=tk.X, pady=4)
        ttk.Label(q_row, text="Quality:", width=10).pack(side=tk.LEFT)
        self.quality_cb = ttk.Combobox(q_row, values=[str(i) for i in range(10, 101, 5)], width=12, state="readonly")
        self.quality_cb.set("70")
        self.quality_cb.pack(side=tk.LEFT, padx=5)

        fmt_row = ttk.Frame(self.parent)
        fmt_row.pack(fill=tk.X, pady=4)
        ttk.Label(fmt_row, text="Format:", width=10).pack(side=tk.LEFT)
        self.format_cb = ttk.Combobox(fmt_row, values=["JPEG", "WEBP"], width=12, state="readonly")
        self.format_cb.set("JPEG")
        self.format_cb.pack(side=tk.LEFT, padx=5)

        opt_row = ttk.Frame(self.parent)
        opt_row.pack(fill=tk.X, pady=4)
        self.optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_row, text="Optimize Output", variable=self.optimize_var).pack(side=tk.LEFT)

        btn_row = ttk.Frame(self.parent)
        btn_row.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_row, 
                   text="Try", 
                   width=10,
                   command=lambda:self.on_try_cb(*self.get_compression_parameters())
                   ).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="Save As", command=self.on_save_as_cb, width=10).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn_row, text="Save", command=self.on_save_cb, width=10).pack(side=tk.RIGHT, padx=2)

