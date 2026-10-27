import os
import math
import statistics
import concurrent.futures
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from image_processor import ImageProcessor
from image_processor_new import ImageProcessor as ImageProcessorNew
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
from components.statusbar import Statusbar
from components.progress_dialog import ProgressDialog


class Workbench:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive JPEG Compression Workbench")
        self.root.geometry("1480x840")

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        self.current_index = -1
        self.source_manager = SourceManager(self.on_source_changed, self.on_destination_changed)

        self.rotation_angle = 0

        self.current_psnr = 0.0
        self.current_ssim = 0.0
        self.saved_session_records = []

        self.current_compression_parameters = {}

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
        self.progress_dialog = ProgressDialog(self.root, title="Please Wait", message="Executing background task...")

    def _setup_shortcuts(self):
        self.root.bind("<Control-Shift-F>", lambda event: self.select_files())
        self.root.bind("<Control-f>", lambda event: self.select_folder())
        self.root.bind("<Control-d>", lambda event: self.select_destination())
        self.root.bind("<Control-s>", lambda event: self.save_current_image())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_as_current_image())

        self.root.bind("<Alt-s>", lambda event: self.viewer.toggle_layout_swap())
        self.root.bind("<Alt-h>", lambda event: self.viewer.toggle_heatmap())
        self.root.bind("<Control-r>", lambda event: self.reset_view())

        self.root.bind("<Control-Left>", lambda event: self.navigate_files(-1))
        self.root.bind("<Control-Right>", lambda event: self.navigate_files(1))

    def _setup_menubar(self):
        menubar_callbacks = {
            "select_files": self.select_files,
            "select_folder": self.select_folder,
            "select_destination": self.select_destination,
            "save":self.save_current_image,
            "save_as": self.save_as_current_image,

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

        self.viewer = Viewer(viewer_container, on_rotate=self.on_rotate_image, on_reset=self.on_reset_view)
        self.viewer.pack(fill=tk.BOTH, expand=True)

    def _setup_right_panel(self, parent):
        right_panel = ttk.Frame(parent, width=350)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)

        # 3A. Compression Panel
        comp_group = ttk.LabelFrame(right_panel, text="Compression Settings", padding=10)
        comp_group.pack(fill=tk.X, pady=(0, 10))
        self.compression_controller = CompressionController(comp_group, self.on_preview, self.on_save, self.on_save_as)
        self._set_current_compression_parameters(*self.compression_controller.get_compression_parameters())

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
        self.statusbar = Statusbar(bottom_frame)
        self.statusbar.set_status("Status: Ready. Please select source files or a folder.", Statusbar.SUCCESS)

    def _set_current_compression_parameters(self, quality, format, optimize):
        self.current_compression_parameters = {
            "quality": quality,
            "format": format,
            "optimize": optimize 
        }
    def _get_current_compression_parameters(self):
        x = self.current_compression_parameters
        return x["quality"], x["format"], x["optimize"]

    def on_source_changed(self, source_mode, source_dir):
        if source_mode == "files":
            t = f"{len(self.source_manager.files)} files selected"
        elif source_mode == "folder":
            t = source_dir

        self.topbar.set_source_label(t)
        self.file_list.populate()

    def on_destination_changed(self, dir_path):
        self.topbar.set_destination_label(dir_path)

    def select_files(self):
        self.source_manager.select_files()
        self.file_list.select(0)
    
    def select_folder(self):
        self.source_manager.select_folder()
        self.file_list.select(0)

    def select_destination(self):
        self.source_manager.select_destination()

    def navigate_files(self, direction):
        new_idx = max(0, min(self.current_index + direction, len(self.file_list.files) - 1))
        self.file_list.select(new_idx)

    def on_file_select(self, index):
        # TODO: in case of source change, and the current index was at 0
        if index == self.current_index and self.current_index!=0:
            return

        self.current_index = index
        file_item = self.source_manager.files[index]

        quality, img_format, optimize = self.compression_controller.get_compression_parameters()
        self._set_current_compression_parameters(quality, format, optimize)

        self.rotation_angle = 0
        self.viewer.zoom_scale = 1.0

        self.show_both(file_item['path'], quality, img_format, optimize, self.rotation_angle)


    def on_save(self, quality, img_format, optimize):
        self.save_current_image()

    def on_save_as(self, quality, img_format, optimize):
        self.save_as_current_image()


    def on_preview(self, quality, format, optimize):
        self._set_current_compression_parameters(quality, format, optimize)
        file_path = self.source_manager.files[self.current_index]['path']

        self.progress_dialog.show(message="Creating compressed preview...")

        self.compress_and_show(file_path, quality, format, optimize, self.rotation_angle,
                               lambda error: self.progress_dialog.close())


    def compress_and_show(self, file_path, quality, img_format, optimize, rotation_angle, callback):
        def _callback(buffer, error):
            if error: 
                messagebox.showerror("Error", f"Failed to process image: {str(error)}")
                self.statusbar.set_status(f"Error: Failed to process image: {str(error)}", Statusbar.ERROR)
                return callback(error)

            compressed_pil_image = Image.open(buffer).copy()
            self.viewer.set_compressed_image(compressed_pil_image)
            self.viewer.render_images()

            callback(None)

        self.compress_async(file_path, quality, img_format, optimize, rotation_angle, _callback)


    def rotate_and_show(self, file_path, rotation_angle, callback):
        def _callback(buffer, error):
            if error: 
                messagebox.showerror("Error", f"Failed to process image: {str(error)}")
                self.statusbar.set_status(f"Error: Failed to process image: {str(error)}", Statusbar.ERROR)
                return callback(error)

            original_pil_image = Image.open(buffer).copy()
            self.viewer.set_original_image(original_pil_image)

            callback(None)

        self.compress_async(file_path, None, None, False, rotation_angle, _callback)


    def show_both(self, file_path, quality, img_format, optimize, rotation_angle):
        self.progress_dialog.show(message="Updating preview...")

        def _compression_callback(error):
            self.progress_dialog.close()

        def _rotation_callback(error):
            if error:
                self.progress_dialog.close()
                return

            self.compress_and_show(file_path, quality, img_format, optimize, rotation_angle, _compression_callback)

        self.rotate_and_show(file_path, rotation_angle, _rotation_callback)


    def compress_async(self, file_path, quality, format, optimize, rotation_angle, callback):
        future = self.executor.submit(
            ImageProcessorNew.process_image,
            file_path, rotation_angle, format, quality, optimize
        )

        def done_callback(f):
            def handle_result():
                buffer, error = f.result()
                return callback(buffer, error)

            self.root.after(0, handle_result)

        future.add_done_callback(done_callback)


    def on_rotate_image(self, angle_delta):
        self.rotation_angle = (self.rotation_angle + angle_delta) % 360
        file_path = self.source_manager.files[self.current_index]['path']
        quality, format, optimize = self._get_current_compression_parameters()

        self.show_both(file_path, quality, format, optimize, self.rotation_angle)


    def on_reset_view(self):
        self.rotation_angle = 0
        self.apply_compression_preview()

    def reset_view(self):
        self.viewer.internal_reset()
        self.on_reset_view()

    def save_current_image(self):
        if not self.source_manager.dest_dir:
            messagebox.showwarning("Destination Missing", "Please select a destination folder first!")
            self.statusbar.set_status("Destination Missing: Please select a destination folder first!", Statusbar.ERROR)
            return

        file_item = self.source_manager.files[self.current_index]

        base_name, _ = os.path.splitext(file_item['rel_path'])
        new_extension = ".webp" if self.current_compression_parameters["quality"] == "WEBP" else ".jpg"
        target_relative_path = base_name + new_extension
        destination_path = os.path.join(self.source_manager.dest_dir, target_relative_path)

        quality, format, optimize = self.compression_controller.get_compression_parameters()

        self._save_async(destination_path, file_item['path'], target_relative_path, quality, format, optimize)

    def save_as_current_image(self):
        file_item = self.source_manager.files[self.current_index]

        default_extension = ".webp" if self.current_compression_parameters["format"] == "WEBP" else ".jpg"
        allowed_filetypes = ("WebP Image", "*.webp") if self.current_compression_parameters["format"] == "WEBP" else ("JPEG Image", "*.jpg;*.jpeg")
        base_name, _ = os.path.splitext(os.path.basename(file_item['rel_path']))
        initial_file = base_name + default_extension

        destination_path = filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=default_extension,
            filetypes=[allowed_filetypes, ("All Files", "*.*")])

        if not destination_path: return

        target_relative_path = os.path.basename(destination_path)
        quality, format, optimize = self.compression_controller.get_compression_parameters()

        self._save_async(destination_path, file_item['path'], target_relative_path, quality, format, optimize)


    def _save_async(self, destination_path, source_path, target_relative_path, quality, format, optimize):
        self.progress_dialog.show(message="Saving...")
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        def _compress_async_callback(buffer, error):
            self.progress_dialog.close()

            if error:
                messagebox.showerror("Error", f"Failed to save image {str(error)}")
                self.statusbar.set_status(f"Error: Failed to save image {str(error)}", Statusbar.ERROR)
                return

            try:
                with open(destination_path, "wb") as f:
                    f.write(buffer.getvalue())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to write file: {str(e)}")
                self.statusbar.set_status(f"Error: Failed to write file {str(e)}", Statusbar.ERROR)
                return

            original_size = os.path.getsize(source_path)
            compressed_size = buffer.getbuffer().nbytes

            self.statusbar.set_status(f"Saved successfully: {target_relative_path}", Statusbar.SUCCESS)

            self.saved_session_records.append({
                'original_file': source_path,
                'output_file': destination_path,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'quality': quality
            })

            self.update_overall_stats_display()
            self.file_list.mark_as_compressed(self.current_index)
            self.statusbar.set_status(f"Saved successfully: {target_relative_path}", Statusbar.SUCCESS)

        self.compress_async(source_path, quality, format, optimize, self.rotation_angle, _compress_async_callback)


    def update_current_stats(self):
        item = self.source_manager.files[self.current_index]
        orig_size = os.path.getsize(item['path'])
        comp_size = current_comp_size
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
        self.curr_stats_text.set_text(info)

    def update_overall_stats_display(self):
        print(self.saved_session_records)
        count = len(self.saved_session_records)
        if count == 0:
            summary = "No files saved in this session yet."
        else:
            total_orig = sum(r['original_size'] for r in self.saved_session_records)
            total_comp = sum(r['compressed_size'] for r in self.saved_session_records)
            overall_pct = (1 - (total_comp / total_orig)) * 100 if total_orig > 0 else 0

            percentages = [
                (1 - (r['compressed_size'] / r['original_size'])) * 100 
                if r['original_size'] > 0 else 0 
                for r in self.saved_session_records
            ]

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
