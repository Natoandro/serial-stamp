import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from PIL import ImageTk


class ConfigPanel(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        # Create a canvas + scrollbar for scrolling the form
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg="#f0f0f0")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Placeholder content
        ttk.Label(
            self.scrollable_frame, text="Configuration", style="Header.TLabel"
        ).pack(pady=20, anchor="w", padx=15)
        ttk.Label(
            self.scrollable_frame,
            text="(Form fields will appear here after loading a config)",
            font=("Segoe UI", 10, "italic"),
            foreground="#666",
        ).pack(pady=5, anchor="w", padx=15)

    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()


class PreviewPanel(ttk.Frame):
    def __init__(
        self, parent, on_resize_callback: Optional[Callable] = None, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.on_resize_callback = on_resize_callback
        self.tk_preview_image: Optional[ImageTk.PhotoImage] = None
        self._setup_ui()

    def _setup_ui(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="Preview", style="Header.TLabel").pack(
            side=tk.LEFT
        )

        # Container for canvas with border
        canvas_container = tk.Frame(self, bg="#ccc", padx=1, pady=1)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg="#e0e0e0", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Placeholder text in canvas
        self.preview_text = self.canvas.create_text(
            200,
            200,
            text="No Project Loaded\nUse File > New or Open",
            fill="#666",
            font=("Segoe UI", 12),
            justify="center",
        )

        # Handle resize centering
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # Keep the text centered
        if hasattr(self, "preview_text"):
            self.canvas.coords(self.preview_text, event.width / 2, event.height / 2)

        if self.on_resize_callback:
            self.on_resize_callback(event)

    def show_message(self, text: str, color: str = "red"):
        self.canvas.delete("all")
        self.preview_text = self.canvas.create_text(
            self.canvas.winfo_width() / 2,
            self.canvas.winfo_height() / 2,
            text=text,
            fill=color,
            justify="center",
            width=300,
        )

    def show_image(self, tk_image: ImageTk.PhotoImage):
        self.tk_preview_image = tk_image  # Keep reference
        self.canvas.delete("all")
        # Center it
        x = self.canvas.winfo_width() / 2
        y = self.canvas.winfo_height() / 2
        self.canvas.create_image(x, y, image=tk_image)

    def get_canvas_size(self) -> tuple[int, int]:
        return self.canvas.winfo_width(), self.canvas.winfo_height()


class BottomBar(ttk.Frame):
    def __init__(
        self, parent, on_load: Callable, on_generate: Callable, *args, **kwargs
    ):
        super().__init__(parent, *args, **kwargs)
        self.on_load = on_load
        self.on_generate = on_generate

        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()

        self._setup_ui()

    def _setup_ui(self):
        # Status Label
        ttk.Label(self, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(
            self, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Buttons
        ttk.Button(self, text="Load Config", command=self.on_load).pack(
            side=tk.RIGHT, padx=5
        )
        self.generate_btn = ttk.Button(
            self,
            text="Generate PDF",
            command=self.on_generate,
            state=tk.DISABLED,
        )
        self.generate_btn.pack(side=tk.RIGHT, padx=5)
