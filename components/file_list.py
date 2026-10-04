import tkinter as tk
from tkinter import ttk


class FileList():
    def __init__(self, parent, files, on_file_select_cb):
        self.parent = parent
        self.files = files
        self.on_file_select_cb = on_file_select_cb
        self.create_widget()

    def create_widget(self):
        list_frame = ttk.Frame(self.parent)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(list_frame, text="Loaded Files:").pack(anchor=tk.W)
        
        self.tree = ttk.Treeview(list_frame, columns=("filename",), show="headings", height=20)
        self.tree.heading("filename", text="File Name")
        self.tree.column("filename", width=200, anchor=tk.W)
        
        self.tree.tag_configure("compressed", foreground="green", font=("Arial", 9, "overstrike"))

        self.tree.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._handle_tree_selection)

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=list_scroll.set)

    def _handle_tree_selection(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            item_id = selected_items[0]
            index = self.tree.index(item_id)
            
            if self.on_file_select_cb:
                self.on_file_select_cb(index)

    def insert(self, v, t):
        self.tree.insert("", "end", values=v, tags=t)
    
    def delete(self, item_id):
        self.tree.delete(item_id)

    def populate(self):
        for item_id in self.tree.get_children():
            self.delete(item_id)

        for item in self.files:
            tags = ("compressed",) if item.get('is_compressed', False) else ()
            self.insert(item["rel_path"], tags)
 
