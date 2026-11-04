import tkinter as tk
from tkinter import ttk

from utility import *
from strings import RESTORE_WIZARD_DESCRIPTION


class RestoreProgressDialog(tk.Toplevel):
    def __init__(self, parent, matched_files, on_mark):
        super().__init__(parent)
        self.parent = parent
        self.matched_files = matched_files
        self.on_mark_cb = on_mark

        # Dialog configuration
        self.title("Restore Previous Session")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        self.geometry("800x520")
        self.minsize(800, 520)

        center_dialog(parent, self)

        # Track selection state for each item (item_id -> bool)
        self.row_states = {}

        self.create_widgets()

    def create_widgets(self):
        # 1. Informational Header Labels
        file_count = len(self.matched_files)

        lbl_info = ttk.Label(
            self,
            text=f"Found {file_count} matching file(s) in the destination folder.",
            font=("Segoe UI", 10, "bold")
        )
        lbl_info.pack(padx=10, pady=(15, 0), anchor="w")

        lbl_desc = ttk.Label(
            self,
            text=RESTORE_WIZARD_DESCRIPTION,

            font=("Segoe UI", 9),
            wraplength=780,
            justify=tk.LEFT
        )
        lbl_desc.pack(padx=10, pady=(0, 10), anchor="w")

        # 2. Treeview with Horizontal & Vertical Scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Configure grid weight for tree_frame to allow smooth resizing/scrolling
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        columns = ("select", "file_name", "rel_path", "source_path", "destination_path", "source_size", "destination_size")

        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        # Define Headings
        self.tree.heading("select", text="Select")
        self.tree.heading("file_name", text="File Name")
        self.tree.heading("rel_path", text="Relative Path")
        self.tree.heading("source_path", text="Source Path")
        self.tree.heading("destination_path", text="Destination Path")
        self.tree.heading("source_size", text="Source Size")
        self.tree.heading("destination_size", text="Destination Size")

        # Define Column Widths, Min-Widths & Stretching
        self.tree.column("select", width=60, minwidth=60, anchor="center", stretch=False)
        self.tree.column("file_name", width=140, minwidth=100, anchor="w", stretch=False)
        self.tree.column("rel_path", width=180, minwidth=120, anchor="w", stretch=False)
        self.tree.column("source_path", width=220, minwidth=150, anchor="w", stretch=False)
        self.tree.column("destination_path", width=220, minwidth=150, anchor="w", stretch=False)
        self.tree.column("source_size", width=90, minwidth=80, anchor="e", stretch=False)
        self.tree.column("destination_size", width=90, minwidth=80, anchor="e", stretch=False)

        # Scrollbars
        vsbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsbar.set, xscrollcommand=hsbar.set)

        # Grid placement for Treeview and Scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsbar.grid(row=0, column=1, sticky="ns")
        hsbar.grid(row=1, column=0, sticky="ew")

        # Populate rows (defaulting all checkboxes to checked / True)
        for item in self.matched_files:
            item_id = self.tree.insert("", tk.END, values=(
                "\u2611",  # Checked box unicode character
                item.get("file_name", ""),
                item.get("rel_path", ""),
                item.get("source_path", ""),
                item.get("destination_path", ""),
                format_size(item.get("source_size", 0)),
                format_size(item.get("destination_size", 0))
            ))
            self.row_states[item_id] = True

        # Bind click event on Treeview for interactive checkboxes
        self.tree.bind("<Button-1>", self._on_tree_click)

        # 3. Master "Select All" Control Frame
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(padx=10, pady=5, fill=tk.X)

        self.select_all_var = tk.BooleanVar(value=True)
        self.chk_select_all = ttk.Checkbutton(
            ctrl_frame, 
            text="Select All", 
            variable=self.select_all_var,
            command=self._toggle_select_all
        )
        self.chk_select_all.pack(side=tk.LEFT)

        # 4. Action Buttons Footer using ttk
        btn_frame = ttk.Frame(self)
        btn_frame.pack(padx=10, pady=(5, 15), fill=tk.X)

        self.btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        self.btn_cancel.pack(side=tk.RIGHT)

        self.btn_mark = ttk.Button(btn_frame, text="Mark Selected", command=self._on_mark_clicked)
        self.btn_mark.pack(side=tk.RIGHT, padx=5)

    def _on_tree_click(self, event):
        """Toggles check state when user clicks on the first column."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":  # First column ('select')
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    current_state = self.row_states.get(item_id, True)
                    new_state = not current_state
                    self.row_states[item_id] = new_state

                    # Update row check visual icon
                    vals = list(self.tree.item(item_id, "values"))
                    vals[0] = "\u2611" if new_state else "\u2610"
                    self.tree.item(item_id, values=vals)

                    # Synchronize Master Checkbox state
                    self._update_select_all_checkbox_state()

    def _toggle_select_all(self):
        """Toggles all row checkboxes based on the Master 'Select All' toggle."""
        state = self.select_all_var.get()
        for item_id in self.tree.get_children():
            self.row_states[item_id] = state
            vals = list(self.tree.item(item_id, "values"))
            vals[0] = "\u2611" if state else "\u2610"
            self.tree.item(item_id, values=vals)

    def _update_select_all_checkbox_state(self):
        """Updates master toggle if individual checkboxes change state."""
        all_checked = all(self.row_states.values())
        if self.select_all_var.get() != all_checked:
            self.select_all_var.set(all_checked)

    def _on_mark_clicked(self):
        """Collects checked file records, triggers callback, and closes dialog."""
        selected_items = []
        for idx, item_id in enumerate(self.tree.get_children()):
            if self.row_states.get(item_id, False):
                selected_items.append(self.matched_files[idx])

        if self.on_mark_cb:
            self.on_mark_cb(selected_items)

        self.destroy()
