import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from image_processor import ImageProcessor  # Adjust import based on your project structure

class Viewer(ttk.Frame):
    """Encapsulates side-by-side canvases, zoom/pan synchronization, layout swapping, rendering, and heatmap controls."""
    def __init__(self, parent, on_rotate, on_reset):
        super().__init__(parent)
        self.on_rotate_cb = on_rotate
        self.on_reset_cb = on_reset
        
        self.zoom_scale = 1.0
        self.swapped = False
        self.showing_heatmap = False
        self.heatmap_multiplier = 5.0  # Default multiplier
        
        # Stored image references for rendering
        self.rotated_orig_img = None
        self.comp_pil_img = None
        self.raw_diff_gray = None

        # Image Tk references to prevent garbage collection
        self.orig_tk = None
        self.preview_tk = None
        
        self._drag_data = {"x": 0, "y": 0}
        self.setup_widgets()

    def set_images(self, rotated_orig_img, comp_pil_img, raw_diff_gray):
        """Stores image references inside the viewer component."""
        self.rotated_orig_img = rotated_orig_img
        self.comp_pil_img = comp_pil_img
        self.raw_diff_gray = raw_diff_gray

    def setup_widgets(self):
        # 1. Headers container
        self.headers_frame = ttk.Frame(self)
        self.headers_frame.pack(fill=tk.X)
        
        self.left_header = ttk.Label(self.headers_frame, text="Original Image", font=("Arial", 10, "bold"))
        self.left_header.pack(side=tk.LEFT, expand=True)
        
        self.right_header = ttk.Label(self.headers_frame, text="Compressed Preview", font=("Arial", 10, "bold"))
        self.right_header.pack(side=tk.RIGHT, expand=True)

        # 2. Canvases Layout
        canvases_frame = ttk.Frame(self)
        canvases_frame.pack(fill=tk.BOTH, expand=True)

        self.v_scrollbar = ttk.Scrollbar(canvases_frame, orient=tk.VERTICAL, command=self.on_v_scroll)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scrollbar = ttk.Scrollbar(canvases_frame, orient=tk.HORIZONTAL, command=self.on_h_scroll)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas_a = tk.Canvas(canvases_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_b = tk.Canvas(canvases_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas_b.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas_a.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.canvas_b.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        for canvas in (self.canvas_a, self.canvas_b):
            canvas.bind("<ButtonPress-1>", self.on_pan_start)
            canvas.bind("<B1-Motion>", self.on_pan_move)

        self.progressbar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progressbar.pack(fill=tk.X, pady=5)

        # 3. Bottom controls toolbar
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill=tk.X, pady=5)

        ttk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=2)
        self.zoom_slider = ttk.Scale(toolbar, from_=0.2, to=4.0, value=1.0, orient=tk.HORIZONTAL, length=100)
        self.zoom_slider.pack(side=tk.LEFT, padx=2)
        self.zoom_slider.bind("<ButtonRelease-1>", lambda e: self.on_zoom_change(float(self.zoom_slider.get())))
        
        ttk.Button(toolbar, text="Reset", command=self.internal_reset).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="↺ -90°", width=5, command=lambda: self.on_rotate_cb(90)).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="90° ↻", width=5, command=lambda: self.on_rotate_cb(-90)).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="180°", width=5, command=lambda: self.on_rotate_cb(180)).pack(side=tk.LEFT, padx=1)
        
        # Heatmap Gain Slider
        self.gain_slider = ttk.Scale(toolbar, from_=1.0, to=20.0, value=5.0, orient=tk.HORIZONTAL, length=100)
        self.gain_slider.pack(side=tk.RIGHT, padx=2)
        self.gain_slider.bind("<ButtonRelease-1>", lambda e: self.on_heatmap_gain_change(float(self.gain_slider.get())))
        ttk.Label(toolbar, text="Heatmap Gain:").pack(side=tk.RIGHT, padx=(10, 2))

        # Utility buttons on the right
        ttk.Button(toolbar, text="🔥 Heatmap", command=self.toggle_heatmap).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar, text="⇄ Swap Layout", command=self.toggle_layout_swap).pack(side=tk.RIGHT, padx=5)

    def on_zoom_change(self, scale):
        self.zoom_scale = scale
        self.render_images()

    def on_heatmap_gain_change(self, gain):
        self.heatmap_multiplier = gain
        if self.showing_heatmap:
            self.render_images()

    def render_images(self):
        if self.rotated_orig_img is None:
            return

        canvas_width = max(self.canvas_a.winfo_width(), 400)
        canvas_height = max(self.canvas_a.winfo_height(), 400)

        w_ratio = canvas_width / self.rotated_orig_img.width
        h_ratio = canvas_height / self.rotated_orig_img.height
        base_scale = min(w_ratio, h_ratio, 1.0)

        current_scale = base_scale * self.zoom_scale
        new_w = int(self.rotated_orig_img.width * current_scale)
        new_h = int(self.rotated_orig_img.height * current_scale)

        orig_res = self.rotated_orig_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        if self.showing_heatmap:
            heatmap_img = ImageProcessor.render_heatmap(self.raw_diff_gray, self.heatmap_multiplier)
            preview_res = heatmap_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        else:
            preview_res = self.comp_pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        self.orig_tk = ImageTk.PhotoImage(orig_res)
        self.preview_tk = ImageTk.PhotoImage(preview_res)

        self.canvas_a.delete("all")
        self.canvas_b.delete("all")

        if self.swapped:
            self.canvas_a.create_image(0, 0, anchor=tk.NW, image=self.preview_tk)
            self.canvas_b.create_image(0, 0, anchor=tk.NW, image=self.orig_tk)
        else:
            self.canvas_a.create_image(0, 0, anchor=tk.NW, image=self.orig_tk)
            self.canvas_b.create_image(0, 0, anchor=tk.NW, image=self.preview_tk)

        self.canvas_a.config(scrollregion=(0, 0, new_w, new_h))
        self.canvas_b.config(scrollregion=(0, 0, new_w, new_h))

    def toggle_heatmap(self):
        self.showing_heatmap = not self.showing_heatmap
        title = "Error Heatmap" if self.showing_heatmap else "Compressed Preview"
        if self.swapped:
            self.left_header.config(text=title)
        else:
            self.right_header.config(text=title)
        self.render_images()

    def toggle_layout_swap(self):
        self.swapped = not self.swapped
        h_text = "Error Heatmap" if self.showing_heatmap else "Compressed Preview"
        if self.swapped:
            self.left_header.config(text=h_text)
            self.right_header.config(text="Original Image")
        else:
            self.left_header.config(text="Original Image")
            self.right_header.config(text=h_text)

        for widget in self.canvas_a.master.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.pack_forget()

        if self.swapped:
            self.canvas_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvas_a.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        else:
            self.canvas_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.canvas_b.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def on_pan_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_pan_move(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        x_fractions = self.canvas_a.xview()
        y_fractions = self.canvas_a.yview()
        
        scroll_region = self.canvas_a.cget("scrollregion")
        if not scroll_region:
            return
        
        _, _, region_w, region_h = map(float, scroll_region.split())
        if region_w <= 0 or region_h <= 0:
            return

        current_x_fraction = x_fractions[0] - (dx / region_w)
        current_y_fraction = y_fractions[0] - (dy / region_h)

        self.canvas_a.xview_moveto(current_x_fraction)
        self.canvas_a.yview_moveto(current_y_fraction)
        self.canvas_b.xview_moveto(current_x_fraction)
        self.canvas_b.yview_moveto(current_y_fraction)

    def on_v_scroll(self, *args):
        self.canvas_a.yview(*args)
        self.canvas_b.yview(*args)

    def on_h_scroll(self, *args):
        self.canvas_a.xview(*args)
        self.canvas_b.xview(*args)

    def start_progress(self):
        self.progressbar.start()

    def stop_progress(self):
        self.progressbar.stop()

    def internal_reset(self):
        self.zoom_slider.set(1.0)
        self.zoom_scale = 1.0

        self.gain_slider.set(5.0)
        self.heatmap_multiplier = 5.0

        if self.swapped:
            self.toggle_layout_swap()

        self.on_reset_cb()
