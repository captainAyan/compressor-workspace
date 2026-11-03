# import os
# import tkinter as tk
# from tkinter import ttk
#
#
# class SessionDataView():
#     def __init__(self, parent):
#         self.parent = parent
#         self.tree = None
#         self.last_records = []
#         self.basename_var = tk.BooleanVar(value=True)
#         self.create_widget()
#
#     def create_widget(self):
#         self.checkbox = ttk.Checkbutton(
#             self.parent,
#             text="Just the File Names",
#             variable=self.basename_var,
#             command=self._on_checkbox_toggle,
#         )
#         self.checkbox.pack(anchor=tk.W, pady=(0, 4))
#
#         columns = ('original_file', 'output_file', 'original_size', 'compressed_size', 'quality')
#
#         tree_frame = ttk.Frame(self.parent)
#         tree_frame.pack(fill=tk.BOTH, expand=True)
#
#         tree_frame.rowconfigure(0, weight=1)
#         tree_frame.columnconfigure(0, weight=1)
#
#         self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
#
#         self.tree.heading('original_file', text='Original File')
#         self.tree.heading('output_file', text='Output File')
#         self.tree.heading('original_size', text='Original Size')
#         self.tree.heading('compressed_size', text='Compressed Size')
#         self.tree.heading('quality', text='Quality')
#
#         self.tree.column('original_file', width=220, minwidth=150, stretch=False, anchor=tk.W)
#         self.tree.column('output_file', width=220, minwidth=150, stretch=False, anchor=tk.W)
#         self.tree.column('original_size', width=110, minwidth=90, stretch=False, anchor=tk.E)
#         self.tree.column('compressed_size', width=110, minwidth=90, stretch=False, anchor=tk.E)
#         self.tree.column('quality', width=80, minwidth=60, stretch=False, anchor=tk.E)
#
#         v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
#         h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
#         self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
#
#         self.tree.grid(row=0, column=0, sticky='nsew')
#         v_scrollbar.grid(row=0, column=1, sticky='ns')
#         h_scrollbar.grid(row=1, column=0, sticky='ew')
#
#     def _on_checkbox_toggle(self):
#         if self.last_records:
#             self.refresh(self.last_records)
#
#     def refresh(self, saved_session_records):
#         self.last_records = saved_session_records
#
#         # Clear existing items
#         for item in self.tree.get_children():
#             self.tree.delete(item)
#
#         show_basename_only = self.basename_var.get()
#
#         for record in saved_session_records:
#             original = record['original_file']
#             output = record['output_file']
#
#             if show_basename_only:
#                 original = os.path.basename(original)
#                 output = os.path.basename(output)
#
#             self.tree.insert('', tk.END, values=(
#                 original,
#                 output,
#                 record['original_size'],
#                 record['compressed_size'],
#                 record['quality']
#             ))

import os
import tkinter as tk
from tkinter import ttk


class SessionDataView:
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        self.last_records = []
        self.basename_var = tk.BooleanVar(value=True)
        self.create_widget()

    def create_widget(self):
        # Configure parent grid
        self.parent.rowconfigure(1, weight=1)
        self.parent.columnconfigure(0, weight=1)

        # Checkbox
        self.checkbox = ttk.Checkbutton(
            self.parent,
            text="Just the File Names",
            variable=self.basename_var,
            command=self._on_checkbox_toggle,
        )
        self.checkbox.grid(row=0, column=0, sticky="w", pady=(0, 4))

        # Treeview container
        tree_frame = ttk.Frame(self.parent)
        tree_frame.grid(row=1, column=0, sticky="nsew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        columns = ('original_file', 'output_file', 'original_size', 'compressed_size', 'quality')

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        self.tree.heading('original_file', text='Original File')
        self.tree.heading('output_file', text='Output File')
        self.tree.heading('original_size', text='Original Size')
        self.tree.heading('compressed_size', text='Compressed Size')
        self.tree.heading('quality', text='Quality')

        self.tree.column('original_file', width=220, minwidth=150, stretch=False, anchor=tk.W)
        self.tree.column('output_file', width=220, minwidth=150, stretch=False, anchor=tk.W)
        self.tree.column('original_size', width=110, minwidth=90, stretch=False, anchor=tk.E)
        self.tree.column('compressed_size', width=110, minwidth=90, stretch=False, anchor=tk.E)
        self.tree.column('quality', width=80, minwidth=60, stretch=False, anchor=tk.E)

        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

    def _on_checkbox_toggle(self):
        if self.last_records:
            self.refresh(self.last_records)

    def refresh(self, session_data):
        self.last_records = session_data

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        show_basename_only = self.basename_var.get()

        for record in session_data:
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
