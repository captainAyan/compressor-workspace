import tkinter as tk
from tkinter import ttk

from components.disabled_text import DisabledText

class Topbar():
    def __init__(self, parent, on_src_files_select_cb, on_src_folder_select_cb, on_dest_folder_select_cb):
        self.parent = parent
        self.on_src_files_select_cb = on_src_files_select_cb
        self.on_src_folder_select_cb = on_src_folder_select_cb
        self.on_dest_folder_select_cb = on_dest_folder_select_cb
        self.create_widget()

    def create_widget(self):
        top_frame = ttk.Frame(self.parent, padding=10)
        top_frame.pack(fill=tk.X)

        src_dest_frame = ttk.LabelFrame(top_frame, text="Source & Destination Selection", padding=10)
        src_dest_frame.pack(side=tk.LEFT)

        ttk.Button(src_dest_frame, text="Select Files", command=self.on_src_files_select_cb).pack(side=tk.LEFT, padx=5)
        ttk.Button(src_dest_frame, text="Select Folder", command=self.on_src_folder_select_cb).pack(side=tk.LEFT, padx=5)

        # TODO turn these into their own components
        self.source_label = DisabledText(src_dest_frame, height=2, width=40)
        self.source_label.pack(side=tk.LEFT, padx=5)
        self.source_label.set_text("Source: None selected")

        ttk.Separator(src_dest_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(src_dest_frame, text="Select Destination", command=self.on_dest_folder_select_cb).pack(side=tk.LEFT, padx=5)

        self.destination_label = DisabledText(src_dest_frame, height=2, width=40)
        self.destination_label.pack(side=tk.LEFT, padx=5)
        self.destination_label.set_text("Destination: None selected")

    def set_source_label(self, text):
        self.source_label.set_text(text)

    def set_destination_label(self, text):
        self.destination_label.set_text(text)

