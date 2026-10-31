import math
import tkinter as tk
from tkinter import ttk

from components.disabled_text import DisabledText


class StatsView:
    def __init__(self, parent):
        self.parent = parent
        self.current_tab = "current"  # Tracks active tab ('current' or 'overall')

        self.create_widget()

    def create_widget(self):
        tab_bar = ttk.Frame(self.parent)
        tab_bar.pack(fill=tk.X, pady=(0, 8))

        self.btn_current = ttk.Button(
            tab_bar,
            text="Current File Stats",
            command=lambda: self.switch_tab("current"),
        )
        self.btn_current.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_overall = ttk.Button(
            tab_bar,
            text="Overall Session Stats",
            command=lambda: self.switch_tab("overall"),
        )
        self.btn_overall.pack(side=tk.LEFT)

        self.content_frame = ttk.Frame(self.parent)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.curr_stats_text = DisabledText(
            self.content_frame, height=10, width=38
        )
        self.curr_stats_text.set_text("No file is selected.")

        self.overall_stats_text = DisabledText(
            self.content_frame, height=10, width=38
        )
        self.overall_stats_text.set_text("No files saved in this session yet.")

        self.switch_tab("current")

    def switch_tab(self, tab_name):
        self.current_tab = tab_name

        # Hide both text widgets first using pack_forget()
        self.curr_stats_text.pack_forget()
        self.overall_stats_text.pack_forget()

        # Show the selected one and update button styling state if desired
        if tab_name == "current":
            self.curr_stats_text.pack(fill=tk.BOTH, expand=True)
            # Optional: You can change button states or style to indicate active tab
            self.btn_current.state(["pressed", "disabled"])
            self.btn_overall.state(["!pressed", "!disabled"])
        else:
            self.overall_stats_text.pack(fill=tk.BOTH, expand=True)
            self.btn_overall.state(["pressed", "disabled"])
            self.btn_current.state(["!pressed", "!disabled"])

    def update_overall_stats(self, count, total_original, total_compressed, overall_pct, mean_pct, median_pct):
        summary = (
            f"Files Saved: {count}\n"
            f"Total Orig: {total_original:.2f} MB\n"
            f"Total Comp: {total_compressed:.2f} MB\n"
            f"Overall Saved: {overall_pct:.1f}%\n"
            f"Mean Compression: {mean_pct:.1f}%\n"
            f"Median Compression: {median_pct:.1f}%"
        )
        self.overall_stats_text.set_text(summary)

    def update_current_stats(self, file_name, original_size, compressed_size, saved_percentage, quality, format, psnr_str, ssim):
        info = (
            f"File: {file_name}\n"
            f"Original Size: {original_size / 1024:.2f} KB\n"
            f"Compressed Size: {compressed_size / 1024:.2f} KB\n"
            f"Saved Space: {saved_percentage:.1f}%\n"
            f"PSNR: {psnr_str}\n"
            f"SSIM: {ssim:.4f}\n"
            f"Config: {format} @ Q={quality}"
        )
        self.curr_stats_text.set_text(info)

