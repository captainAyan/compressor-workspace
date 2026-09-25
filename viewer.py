import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class Viewer(ttk.Frame):
    """Encapsulates side-by-side canvases, zoom/pan synchronization, layout swapping, and heatmap controls."""
    def __init__(self, parent, on_zoom_change, on_rotate, on_reset, on_toggle_heatmap, on_heatmap_gain_change):
        super().__init__(parent)
        self.on_zoom_change_cb = on_zoom_change
        self.on_rotate_cb = on_rotate
        self.on_reset_cb = on_reset
        self.on_toggle_heatmap_cb = on_toggle_heatmap
        self.on_heatmap_gain_change_cb = on_heatmap_gain_change
        
        self.zoom_scale = 1.0
        self.rotation_angle = 0
        self.swapped = False
        self.showing_heatmap = False
        
        self._drag_data = {"x": 0, "y": 0}
        self.setup_widgets()

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

        # 3. Bottom controls toolbar
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill=tk.X, pady=5)

        ttk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=2)
        self.zoom_slider = ttk.Scale(toolbar, from_=0.2, to=4.0, value=1.0, orient=tk.HORIZONTAL, length=100)
        self.zoom_slider.pack(side=tk.LEFT, padx=2)
        self.zoom_slider.bind("<ButtonRelease-1>", lambda e: self.on_zoom_change_cb(float(self.zoom_slider.get())))
        
        ttk.Button(toolbar, text="Reset", command=self.on_reset_cb).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="↺ -90°", width=5, command=lambda: self.on_rotate_cb(-90)).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="90° ↻", width=5, command=lambda: self.on_rotate_cb(90)).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="180°", width=5, command=lambda: self.on_rotate_cb(180)).pack(side=tk.LEFT, padx=1)
        
        # Heatmap Gain Slider
        self.gain_slider = ttk.Scale(toolbar, from_=1.0, to=20.0, value=5.0, orient=tk.HORIZONTAL, length=100)
        self.gain_slider.pack(side=tk.RIGHT, padx=2)
        self.gain_slider.bind("<ButtonRelease-1>", lambda e: self.on_heatmap_gain_change_cb(float(self.gain_slider.get())))
        ttk.Label(toolbar, text="Heatmap Gain:").pack(side=tk.RIGHT, padx=(10, 2))

        # Utility buttons on the right
        ttk.Button(toolbar, text="🔥 Heatmap", command=self.toggle_heatmap).pack(side=tk.RIGHT, padx=5)
        ttk.Button(toolbar, text="⇄ Swap Layout", command=self.toggle_layout_swap).pack(side=tk.RIGHT, padx=5)

    def toggle_heatmap(self):
        self.showing_heatmap = not self.showing_heatmap
        title = "Error Heatmap" if self.showing_heatmap else "Compressed Preview"
        if self.swapped:
            self.left_header.config(text=title)
        else:
            self.right_header.config(text=title)
        self.on_toggle_heatmap_cb()

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



