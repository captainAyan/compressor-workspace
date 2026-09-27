import os
import math
import statistics
import concurrent.futures
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from viewer import Viewer
from image_processor import ImageProcessor

from utility import disabled_text_view_updater

class Workbench:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive JPEG Compression Workbench")
        self.root.geometry("1480x840")

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        self.source_mode = None
        self.source_dir = ""
        self.dest_dir = ""
        self.file_items = []
        self.current_index = 0

        self.zoom_scale = 1.0
        self.rotation_angle = 0
        self.heatmap_multiplier = 5.0

        self.current_comp_buffer = None
        self.current_comp_size = 0
        self.current_psnr = 0.0
        self.current_ssim = 0.0
        self.saved_session_records = []

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        self._setup_menubar()
        self._setup_top_bar()
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        self._setup_file_list(main_frame)
        self._setup_viewer_panel(main_frame)
        self._setup_right_panel(main_frame)
        self._setup_bottom_bar()

    def setup_shortcuts(self):
        self.root.bind("<Alt-s>", lambda event: self.viewer.toggle_layout_swap())
        self.root.bind("<Alt-h>", lambda event: self.viewer.toggle_heatmap())
        self.root.bind("<Control-r>", lambda event: self.reset_view())

    def _setup_menubar(self):
        # TODO make it work
        menubar = tk.Menu(self.root)

        # 1. File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Files", command=lambda: self.select_files())
        file_menu.add_command(label="Select Folder", command=lambda: self.select_folder())
        file_menu.add_command(label="Select Destination", command=lambda: self.select_destination())
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # 2. View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Swap View", accelerator="Alt+S", command=lambda: self.viewer.toggle_layout_swap())
        view_menu.add_command(label="View Heatmap", accelerator="Alt+H", command=lambda: self.viewer.toggle_heatmap())
        view_menu.add_separator()
        view_menu.add_command(label="Reset View", accelerator="Ctrl+R", command=lambda: self.reset_view())
        menubar.add_cascade(label="View", menu=view_menu)

        # 3. Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: placeholder_action("About"))
        help_menu.add_command(label="Shortcuts", command=lambda: placeholder_action("Shortcuts"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def _setup_top_bar(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        src_dest_frame = ttk.LabelFrame(top_frame, text="Source & Destination Selection", padding=10)
        src_dest_frame.pack(side=tk.LEFT)

        ttk.Button(src_dest_frame, text="Select Files", command=self.select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(src_dest_frame, text="Select Folder", command=self.select_folder).pack(side=tk.LEFT, padx=5)

        self.source_label = tk.Text(src_dest_frame, height=2, width=40, wrap=tk.WORD, bg="#f4f4f4", relief=tk.FLAT)
        self.source_label.pack(side=tk.LEFT, padx=5)
        disabled_text_view_updater(self.source_label, "Source: None selected")

        ttk.Separator(src_dest_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(src_dest_frame, text="Select Destination", command=self.select_destination).pack(side=tk.LEFT, padx=5)
        self.dest_label = tk.Text(src_dest_frame, height=2, width=40, wrap=tk.WORD, bg="#f4f4f4", relief=tk.FLAT)
        self.dest_label.pack(side=tk.LEFT, padx=5)
        disabled_text_view_updater(self.dest_label, "Destination: None selected")

    def _setup_file_list(self, parent):
        list_frame = ttk.Frame(parent)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        ttk.Label(list_frame, text="Loaded Files:").pack(anchor=tk.W)
        
        # Initialize Treeview
        self.file_tree = ttk.Treeview(list_frame, columns=("filename",), show="headings", height=20)
        self.file_tree.heading("filename", text="File Name")
        self.file_tree.column("filename", width=200, anchor=tk.W)
        
        # Configure a tag for files that have been compressed and saved
        self.file_tree.tag_configure("compressed", foreground="gray", font=("Arial", 9, "overstrike"))
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)

        # Attach scrollbar
        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.config(yscrollcommand=list_scroll.set)

    def _setup_viewer_panel(self, parent):
        viewer_container = ttk.Frame(parent)
        viewer_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.viewer = Viewer(
            viewer_container, 
            on_zoom_change=self.on_zoom_change, 
            on_rotate=self.rotate_image, 
            on_reset=self.reset_view,
            on_toggle_heatmap=self.render_images,
            on_heatmap_gain_change=self.on_heatmap_gain_change
        )
        self.viewer.pack(fill=tk.BOTH, expand=True)

    def _setup_right_panel(self, parent):
        right_panel = ttk.Frame(parent, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)

        # 3A. Compression Panel
        comp_group = ttk.LabelFrame(right_panel, text="Compression Settings", padding=10)
        comp_group.pack(fill=tk.X, pady=(0, 10))

        q_row = ttk.Frame(comp_group)
        q_row.pack(fill=tk.X, pady=4)
        ttk.Label(q_row, text="Quality:", width=10).pack(side=tk.LEFT)
        self.quality_cb = ttk.Combobox(q_row, values=[str(i) for i in range(10, 101, 5)], width=12, state="readonly")
        self.quality_cb.set("70")
        self.quality_cb.pack(side=tk.LEFT, padx=5)

        fmt_row = ttk.Frame(comp_group)
        fmt_row.pack(fill=tk.X, pady=4)
        ttk.Label(fmt_row, text="Format:", width=10).pack(side=tk.LEFT)
        self.format_cb = ttk.Combobox(fmt_row, values=["JPEG", "WEBP"], width=12, state="readonly")
        self.format_cb.set("JPEG")
        self.format_cb.pack(side=tk.LEFT, padx=5)

        opt_row = ttk.Frame(comp_group)
        opt_row.pack(fill=tk.X, pady=4)
        self.optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt_row, text="Optimize Output", variable=self.optimize_var).pack(side=tk.LEFT)

        btn_row = ttk.Frame(comp_group)
        btn_row.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_row, text="Try", command=self.apply_compression_preview, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="Save", command=self.save_current_image, width=10).pack(side=tk.RIGHT, padx=2)

        # 3B. Current Stats Panel
        curr_group = ttk.LabelFrame(right_panel, text="Current File Stats & Metrics", padding=10)
        curr_group.pack(fill=tk.X, pady=(0, 10))
        
        self.curr_stats_text = tk.Text(curr_group, height=10, width=38, wrap=tk.WORD, bg="#f4f4f4", relief=tk.FLAT)
        self.curr_stats_text.pack(fill=tk.BOTH)
        disabled_text_view_updater(self.curr_stats_text, "No file is selected.")

        # 3C. Overall Stats Panel
        overall_group = ttk.LabelFrame(right_panel, text="Overall Session Stats", padding=10)
        overall_group.pack(fill=tk.BOTH, expand=True)

        self.overall_stats_text = tk.Text(overall_group, height=9, width=38, wrap=tk.WORD, bg="#f4f4f4", relief=tk.FLAT)
        self.overall_stats_text.pack(fill=tk.BOTH, expand=True)
        self.update_overall_stats_display()

    def _setup_bottom_bar(self):
        bottom_frame = ttk.Frame(self.root, padding=5)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.bottom_stats_label = ttk.Label(bottom_frame, text="Status: Ready. Please select source files or a folder.", font=("Arial", 9))
        self.bottom_stats_label.pack(side=tk.LEFT)

    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp")])
        if file_paths:
            self.source_mode = "files"
            self.source_dir = ""
            # self.source_label.config(text=f"{len(file_paths)} files selected")
            disabled_text_view_updater(self.source_label, f"{len(file_paths)} files selected")

            self.file_items = [{'path': p, 'compressed': False, 'rel_path': os.path.basename(p)} for p in file_paths]
            self.populate_file_list()

    def select_folder(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.source_mode = "folder"
            self.source_dir = dir_path
            disabled_text_view_updater(self.source_label, dir_path)

            self.file_items = []
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, dir_path)
                        self.file_items.append({'path': full_p, 'rel_path': rel_p})
            self.populate_file_list()

    def select_destination(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.dest_dir = dir_path
            disabled_text_view_updater(self.dest_label, dir_path)

    def populate_file_list(self):
        for item_id in self.file_tree.get_children():
            self.file_tree.delete(item_id)
            
        # Insert files and apply tags based on their status
        for item in self.file_items:
            # Check if the item is already compressed (adjust key to match your dictionary structure)
            tags = ("compressed",) if item.get('is_compressed', False) else ()
            
            self.file_tree.insert("", "end", values=(item['rel_path'],), tags=tags)
            
        # Select the first item if items exist
        # children = self.file_tree.get_children()
        # if children:
        #     first_item_id = children[0]
        #     self.file_tree.selection_set(first_item_id)
        #     self.load_current_item(0)

    def on_file_select(self, event):
        selected_items = self.file_tree.selection()
        if selected_items:
            item_id = selected_items[0]
            index = self.file_tree.index(item_id)
            self.load_current_item(index)

    def load_current_item(self, index):
        self.current_index = index
        item = self.file_items[index]
        self.rotation_angle = 0
        self.bottom_stats_label.config(text=f"Status: Loading {item['rel_path']}...")
        self.run_processing(item['path'])

    def apply_compression_preview(self):
        if not self.file_items:
            return
        item = self.file_items[self.current_index]
        self.bottom_stats_label.config(text=f"Status: Compressing {item['rel_path']}...")

        self.run_processing(item['path'])

    def run_processing(self, file_path):
        self.viewer.start_progress()

        quality = int(self.quality_cb.get())
        img_format = self.format_cb.get()
        optimize = self.optimize_var.get()

        future = self.executor.submit(
            ImageProcessor.process_image, 
            file_path, self.rotation_angle, img_format, quality, optimize
        )
        future.add_done_callback(lambda f: self.root.after(0, lambda: self._on_image_loaded(f)))

    def _on_image_loaded(self, future):
        buffer, comp_size, comp_img, raw_diff_gray, rotated_orig, psnr, ssim, error = future.result()
        if error:
            messagebox.showerror("Error", f"Failed to process image: {error}")
            return

        self.current_comp_buffer = buffer
        self.current_comp_size = comp_size
        self.comp_pil_img = comp_img
        self.raw_diff_gray = raw_diff_gray
        self.rotated_orig_img = rotated_orig
        self.current_psnr = psnr
        self.current_ssim = ssim

        self.render_images()
        self.update_current_stats()
        self.bottom_stats_label.config(text="Status: Ready.")

        self.viewer.stop_progress()

    def render_images(self):
        if not hasattr(self, 'rotated_orig_img'):
            return

        canvas_width = max(self.viewer.canvas_a.winfo_width(), 400)
        canvas_height = max(self.viewer.canvas_a.winfo_height(), 400)

        w_ratio = canvas_width / self.rotated_orig_img.width
        h_ratio = canvas_height / self.rotated_orig_img.height
        base_scale = min(w_ratio, h_ratio, 1.0)

        current_scale = base_scale * self.zoom_scale
        new_w = int(self.rotated_orig_img.width * current_scale)
        new_h = int(self.rotated_orig_img.height * current_scale)

        orig_res = self.rotated_orig_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        if self.viewer.showing_heatmap:
            # Generate heatmap instantly from cached difference buffer using slider multiplier
            heatmap_img = ImageProcessor.render_heatmap(self.raw_diff_gray, self.heatmap_multiplier)
            preview_res = heatmap_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            preview_res = self.comp_pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        self.orig_tk = ImageTk.PhotoImage(orig_res)
        self.preview_tk = ImageTk.PhotoImage(preview_res)

        self.viewer.canvas_a.delete("all")
        self.viewer.canvas_b.delete("all")

        if self.viewer.swapped:
            self.viewer.canvas_a.create_image(0, 0, anchor=tk.NW, image=self.preview_tk)
            self.viewer.canvas_b.create_image(0, 0, anchor=tk.NW, image=self.orig_tk)
        else:
            self.viewer.canvas_a.create_image(0, 0, anchor=tk.NW, image=self.orig_tk)
            self.viewer.canvas_b.create_image(0, 0, anchor=tk.NW, image=self.preview_tk)

        self.viewer.canvas_a.config(scrollregion=(0, 0, new_w, new_h))
        self.viewer.canvas_b.config(scrollregion=(0, 0, new_w, new_h))

    def on_zoom_change(self, scale):
        self.zoom_scale = scale
        self.render_images()

    def on_heatmap_gain_change(self, gain):
        self.heatmap_multiplier = gain
        if self.viewer.showing_heatmap:
            self.render_images()

    def rotate_image(self, angle_delta):
        self.rotation_angle = (self.rotation_angle + angle_delta) % 360
        self.apply_compression_preview()

    def reset_view(self):
        self.zoom_scale = 1.0
        self.viewer.zoom_slider.set(1.0)
        self.heatmap_multiplier = 5.0
        self.viewer.gain_slider.set(5.0)
        self.rotation_angle = 0
        self.apply_compression_preview()

    def save_current_image(self):
        if not self.dest_dir:
            messagebox.showwarning("Destination Missing", "Please select a destination folder first!")
            return
        if not self.current_comp_buffer:
            messagebox.showwarning("No Data", "No compressed preview buffer available. Click 'Try' first.")
            return

        item = self.file_items[self.current_index]
        base_name, _ = os.path.splitext(item['rel_path'])
        new_ext = ".webp" if self.format_cb.get() == "WEBP" else ".jpg"
        target_rel_path = base_name + new_ext

        dest_path = os.path.join(self.dest_dir, target_rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        def background_save():
            with open(dest_path, "wb") as f:
                f.write(self.current_comp_buffer.getvalue())
            return dest_path

        future = self.executor.submit(background_save)
        future.add_done_callback(lambda f: self.root.after(0, lambda: self._on_save_complete(f, item, target_rel_path)))

    def _on_save_complete(self, future, item, target_rel_path):
        saved_path = future.result()
        orig_size = os.path.getsize(item['path'])
        comp_size = self.current_comp_size
        pct_saved = (1 - (comp_size / orig_size)) * 100 if orig_size > 0 else 0

        self.saved_session_records.append({
            'orig_size': orig_size,
            'comp_size': comp_size,
            'pct_saved': pct_saved
        })

        self.update_overall_stats_display()
        self.bottom_stats_label.config(text=f"Saved successfully: {target_rel_path}")

    def update_current_stats(self):
        item = self.file_items[self.current_index]
        orig_size = os.path.getsize(item['path'])
        comp_size = self.current_comp_size
        saved_pct = (1 - (comp_size / orig_size)) * 100 if orig_size > 0 else 0

        psnr_str = f"{self.current_psnr:.2f} dB" if not math.isinf(self.current_psnr) else "Inf dB"

        info = (
            f"File: {item['rel_path']}\n"
            f"Original Size: {orig_size / 1024:.2f} KB\n"
            f"Compressed Size: {comp_size / 1024:.2f} KB\n"
            f"Saved Space: {saved_pct:.1f}%\n"
            f"PSNR: {psnr_str}\n"
            f"SSIM: {self.current_ssim:.4f}\n"
            f"Config: {self.format_cb.get()} @ Q={self.quality_cb.get()}"
        )
        disabled_text_view_updater(self.curr_stats_text, info)

    def update_overall_stats_display(self):
        count = len(self.saved_session_records)
        if count == 0:
            summary = "No files saved in this session yet."
        else:
            total_orig = sum(r['orig_size'] for r in self.saved_session_records)
            total_comp = sum(r['comp_size'] for r in self.saved_session_records)
            overall_pct = (1 - (total_comp / total_orig)) * 100 if total_orig > 0 else 0
            
            percentages = [r['pct_saved'] for r in self.saved_session_records]
            mean_pct = statistics.mean(percentages)
            median_pct = statistics.median(percentages)

            summary = (
                f"Files Saved: {count}\n"
                f"Total Orig: {total_orig / (1024*1024):.2f} MB\n"
                f"Total Comp: {total_comp / (1024*1024):.2f} MB\n"
                f"Overall Saved: {overall_pct:.1f}%\n"
                f"Mean Compression: {mean_pct:.1f}%\n"
                f"Median Compression: {median_pct:.1f}%"
            )
        disabled_text_view_updater(self.overall_stats_text, summary)
