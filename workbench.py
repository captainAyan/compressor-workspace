import os
import math
import statistics
import concurrent.futures
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from image_processor import ImageProcessor
from source_manager import SourceManager
from strings import ABOUT_DIALOG, SHORTCUT_DIALOG
from utility import *

from components.viewer import Viewer
from components.menu import Menubar
from components.topbar import Topbar
from components.dialog import show_info_dialog
from components.disabled_text import DisabledText
from components.compression_controller import CompressionController
from components.file_list import FileList


class Workbench:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive JPEG Compression Workbench")
        self.root.geometry("1480x840")

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        self.current_index = 0
        self.source_manager = SourceManager(self.on_source_changed, self.on_destination_changed)

        self.zoom_scale = 1.0
        self.rotation_angle = 0
        self.heatmap_multiplier = 5.0

        self.current_comp_buffer = None
        self.current_comp_size = 0
        self.current_psnr = 0.0
        self.current_ssim = 0.0
        self.saved_session_records = []

        self._setup_ui()
        self._setup_shortcuts()

    def _setup_ui(self):
        self._setup_menubar()
        self._setup_top_bar()
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5)

        self._setup_file_list(main_frame)
        self._setup_viewer_panel(main_frame)
        self._setup_right_panel(main_frame)
        self._setup_bottom_bar()

    def _setup_shortcuts(self):
        self.root.bind("<Alt-s>", lambda event: self.viewer.toggle_layout_swap())
        self.root.bind("<Alt-h>", lambda event: self.viewer.toggle_heatmap())
        self.root.bind("<Control-r>", lambda event: self.reset_view())
        self.root.bind("<Control-Shift-F>", lambda event: self.select_files())
        self.root.bind("<Control-f>", lambda event: self.select_folder())
        self.root.bind("<Control-d>", lambda event: self.select_destination())

    def _setup_menubar(self):
        menubar_callbacks = {
            "select_files": self.select_files,
            "select_folder": self.select_folder,
            "select_destination": self.select_destination,
            "swap_view": lambda: self.viewer.toggle_layout_swap(),
            "toggle_heatmap": lambda: self.viewer.toggle_heatmap(),
            "reset_view": self.reset_view,
            "about_view_action": lambda: show_info_dialog(self.root, "About", ABOUT_DIALOG),
            "shortcuts_view_action": lambda: show_info_dialog(self.root, "Shortcuts", SHORTCUT_DIALOG)
        }
        self.menubar = Menubar(self.root, menubar_callbacks)

    def _setup_top_bar(self):
        self.topbar = Topbar(self.root, self.select_files, self.select_folder, self.select_destination)

    def _setup_file_list(self, parent):
        self.file_list = FileList(parent, self.source_manager.files, self.on_file_select)

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
        self.compression_controller = CompressionController(comp_group, self.on_try, self.on_save)

        # 3B. Current Stats Panel
        curr_group = ttk.LabelFrame(right_panel, text="Current File Stats & Metrics", padding=10)
        curr_group.pack(fill=tk.X, pady=(0, 10))

        self.curr_stats_text = DisabledText(curr_group, height=10, width=38)
        self.curr_stats_text.pack(fill=tk.BOTH)
        self.curr_stats_text.set_text("No file is selected.")

        # 3C. Overall Stats Panel
        overall_group = ttk.LabelFrame(right_panel, text="Overall Session Stats", padding=10)
        overall_group.pack(fill=tk.BOTH, expand=True)

        self.overall_stats_text = DisabledText(overall_group, height=9, width=38)
        self.overall_stats_text.pack(fill=tk.BOTH, expand=True)
        self.update_overall_stats_display()

    def _setup_bottom_bar(self):
        bottom_frame = ttk.Frame(self.root, padding=5)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        self.bottom_stats_label = ttk.Label(bottom_frame, text="Status: Ready. Please select source files or a folder.", font=("Arial", 9))
        self.bottom_stats_label.pack(side=tk.LEFT)

    def on_source_changed(self, source_mode, source_dir):
        self.topbar.set_source_label(source_label_helper(source_mode, source_dir, len(self.source_manager.files)))
        self.file_list.populate()

    def on_destination_changed(self, dir_path):
        self.topbar.set_destination_label(dir_path)

    def select_files(self):
        self.source_manager.select_files()
    
    def select_folder(self):
        self.source_manager.select_folder()

    def select_destination(self):
        self.source_manager.select_destination()

    def on_file_select(self, index):
        # selected_items = self.file_list.tree.selection()
        # if selected_items:
        #     item_id = selected_items[0]
        #     index = self.file_list.tree.index(item_id)
        #     self.load_current_item(index)
        print(index)
        self.load_current_item(index)

    def load_current_item(self, index):
        self.current_index = index
        item = self.source_manager.files[index]
        self.rotation_angle = 0
        self.bottom_stats_label.config(text=f"Status: Loading {item['rel_path']}...")
        self.run_processing(item['path'])

    def on_try(self, quality, img_format, optimize):
        print("trying")

    def on_save(self):
        print("saving")

    def apply_compression_preview(self):
        if not self.source_manager.files:
            return
        item = self.source_manager.files[self.current_index]
        self.bottom_stats_label.config(text=f"Status: Compressing {item['rel_path']}...")

        self.run_processing(item['path'])

    def run_processing(self, file_path):
        self.viewer.start_progress()

        quality, img_format, optimize = self.compression_controller.get_compression_parameters()

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
        item = self.source_manager.files[self.current_index]
        orig_size = os.path.getsize(item['path'])
        comp_size = self.current_comp_size
        saved_pct = (1 - (comp_size / orig_size)) * 100 if orig_size > 0 else 0

        quality, img_format, optimize = self.compression_controller.get_compression_parameters()

        psnr_str = f"{self.current_psnr:.2f} dB" if not math.isinf(self.current_psnr) else "Inf dB"

        info = (
            f"File: {item['rel_path']}\n"
            f"Original Size: {orig_size / 1024:.2f} KB\n"
            f"Compressed Size: {comp_size / 1024:.2f} KB\n"
            f"Saved Space: {saved_pct:.1f}%\n"
            f"PSNR: {psnr_str}\n"
            f"SSIM: {self.current_ssim:.4f}\n"
            f"Config: {img_format} @ Q={quality}"
        )
        # disabled_text_view_updater(self.curr_stats_text, info)
        self.curr_stats_text.set_text(info)

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
        self.overall_stats_text.set_text(summary)
