import os
import tkinter as tk
from tkinter import ttk


class SessionDataView():
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        self.last_records = []
        self.basename_var = tk.BooleanVar(value=False)
        self.create_widget()

    def create_widget(self):

        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 1. Checkbox option atop the list
        self.checkbox = ttk.Checkbutton(
            main_frame,
            text="Just the File Names",
            variable=self.basename_var,
            command=self._on_checkbox_toggle,
        )
        self.checkbox.pack(anchor=tk.W, pady=(0, 6))


        # 2. Container for treeview and scrollbars
        columns = ('original_file', 'output_file', 'original_size', 'compressed_size', 'quality')

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid weight for tree_frame so scrollbars stay pinned to edges
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        # Configure column headings
        self.tree.heading('original_file', text='Original File')
        self.tree.heading('output_file', text='Output File')
        self.tree.heading('original_size', text='Original Size')
        self.tree.heading('compressed_size', text='Compressed Size')
        self.tree.heading('quality', text='Quality')

        # Configure columns with stretch=True for paths so they don't get cut off
        self.tree.column('original_file', width=220, minwidth=150, stretch=False, anchor=tk.W)
        self.tree.column('output_file', width=220, minwidth=150, stretch=False, anchor=tk.W)
        self.tree.column('original_size', width=110, minwidth=90, stretch=False, anchor=tk.E)
        self.tree.column('compressed_size', width=110, minwidth=90, stretch=False, anchor=tk.E)
        self.tree.column('quality', width=80, minwidth=60, stretch=False, anchor=tk.CENTER)

        # Vertical and Horizontal Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid layout for precise control over treeview + scrollbars alignment
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

    def _on_checkbox_toggle(self):
        if self.last_records:
            self.refresh(self.last_records)

    def refresh(self, saved_session_records):
        self.last_records = saved_session_records

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        show_basename_only = self.basename_var.get()

        for record in saved_session_records:
            original = record['original_file']
            output = record['output_file']

            if show_basename_only:
                original = os.path.basename(original)
                output = os.path.basename(output)

            self.tree.insert('', tk.END, values=(
                original,
                output,
                record['original_size'],
                record['compressed_size'],
                record['quality']
            ))

