import os
from tkinter import filedialog

class SourceManager:
    def __init__(self, on_source_changed_cb, on_destination_changed_cb):
        self.files = []
        self.source_mode = ""
        self.source_dir = ""
        self.dest_dir = ""
        
        # Save callbacks for later use
        self.on_source_changed_cb = on_source_changed_cb
        self.on_destination_changed_cb = on_destination_changed_cb

    def select_files(self):
        """Opens file dialog, updates internal files state, and notifies UI."""
        file_paths = filedialog.askopenfilenames(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")]
        )
        if file_paths:
            self.source_mode = "files"
            self.source_dir = ""
            
            # Update internal state (in place)
            self.files.clear()
            self.files.extend([
                {'path': p, 'compressed': False, 'rel_path': os.path.basename(p)} 
                for p in file_paths
            ])
            
            # Notify UI via callback
            if self.on_source_changed_cb:
                self.on_source_changed_cb(self.source_mode, self.source_dir)

    def select_folder(self):
        """Opens folder dialog, walks directory, updates internal files state, and notifies UI."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.source_mode = "folder"
            self.source_dir = dir_path
            
            # Update internal state (in place)
            self.files.clear()
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, dir_path)
                        self.files.append({'path': full_p, 'compressed': False, 'rel_path': rel_p})
                        
            # Notify UI via callback
            if self.on_source_changed_cb:
                self.on_source_changed_cb(self.source_mode, self.source_dir)

    def select_destination(self):
        """Opens destination dialog and notifies UI."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.dest_dir = dir_path
            if self.on_destination_changed_cb:
                self.on_destination_changed_cb(dir_path)
