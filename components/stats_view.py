import math
import tkinter as tk
from tkinter import ttk

from components.disabled_text import DisabledText
from utility import format_size


class StatsView:
    def __init__(self, parent):
        self.parent = parent
        self.create_widget()

    def create_widget(self):
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.preview_stats_text = DisabledText(
            self.notebook, height=10, width=38, bg="#ffffff"
        )
        self.preview_stats_text.set_text("No file is selected.")

        self.overall_stats_text = DisabledText(
            self.notebook, height=10, width=38, bg="#ffffff"
        )
        self.overall_stats_text.set_text("No files saved in this session yet.")

        self.notebook.add(self.preview_stats_text, text="Preview Stats")
        self.notebook.add(self.overall_stats_text, text="Overall Session Stats")

    def switch_tab(self, tab_name):
        # Programmatically switch tabs if needed elsewhere in your code
        if tab_name == "preview":
            self.notebook.select(self.preview_stats_text)
        else:
            self.notebook.select(self.overall_stats_text)

    def update_overall_stats(self, count, total_original, total_compressed, overall_pct, mean_pct, median_pct):
        summary = (
            f"Files Saved: {count}\n"
            f"Total Orig: {format_size(total_original)}\n"
            f"Total Comp: {format_size(total_compressed)}\n"
            f"Overall Saved: {overall_pct:.1f}%\n"
            f"Mean Compression: {mean_pct:.1f}%\n"
            f"Median Compression: {median_pct:.1f}%"
        )
        self.overall_stats_text.set_text(summary)

    def update_preview_stats(self, file_name, original_size, compressed_size, saved_percentage, quality, format, psnr_str, ssim):
        info = (
            f"File: {file_name}\n"
            f"Original Size: {format_size(original_size)}\n"
            f"Compressed Size: {format_size(compressed_size)}\n"
            f"Saved Space: {saved_percentage:.1f}%\n"
            f"PSNR: {psnr_str}\n"
            f"SSIM: {ssim:.4f}\n"
            f"Config: {format} @ Q={quality}"
        )
        self.preview_stats_text.set_text(info)
