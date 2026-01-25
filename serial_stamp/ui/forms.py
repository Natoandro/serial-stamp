import tkinter as tk
from tkinter import ttk
from typing import Callable

from serial_stamp.models import Spec


class FormBuilder:
    def __init__(
        self,
        parent: ttk.Frame,
        spec: Spec,
        on_change_callback: Callable[[], None],
        on_browse_image_callback: Callable[[], None],
    ):
        self.parent = parent
        self.spec = spec
        self.on_change_callback = on_change_callback
        self.on_browse_image_callback = on_browse_image_callback
        self.vars: dict[str, tk.Variable] = {}

    def build(self) -> dict[str, tk.Variable]:
        self._build_general_settings()
        self._build_layout_settings()
        self._build_text_elements()
        self._build_parameters()
        return self.vars

    def _on_change(self, *args):
        self.on_change_callback()

    def _add_separator(self):
        ttk.Frame(self.parent, height=2, style="TFrame").pack(fill=tk.X, pady=10)

    def _build_general_settings(self):
        gen_frame = ttk.LabelFrame(self.parent, text="General Settings")
        gen_frame.pack(fill=tk.X, padx=15, pady=(20, 10))

        # Source Image
        self.vars["source_image"] = tk.StringVar(value=self.spec.source_image)
        self.vars["source_image"].trace_add("write", self._on_change)

        f = ttk.Frame(gen_frame)
        f.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(f, text="Source Image", width=15).pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=self.vars["source_image"]).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
        )
        ttk.Button(f, text="Browse...", command=self.on_browse_image_callback).pack(
            side=tk.LEFT
        )

        # Stack Size
        self.vars["stack_size"] = tk.IntVar(value=self.spec.stack_size)
        self.vars["stack_size"].trace_add("write", self._on_change)

        f = ttk.Frame(gen_frame)
        f.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(f, text="Stack Size", width=15).pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=self.vars["stack_size"]).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

    def _build_layout_settings(self):
        layout_frame = ttk.LabelFrame(self.parent, text="Layout")
        layout_frame.pack(fill=tk.X, padx=15, pady=10)

        # Grid Size
        layout = self.spec.layout

        grid_frame = ttk.Frame(layout_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(grid_frame, text="Grid Size (WxH)", width=15).pack(side=tk.LEFT)

        self.vars["grid_w"] = tk.IntVar(value=layout.grid_size[0])
        self.vars["grid_h"] = tk.IntVar(value=layout.grid_size[1])
        self.vars["grid_w"].trace_add("write", self._on_change)
        self.vars["grid_h"].trace_add("write", self._on_change)

        ttk.Entry(grid_frame, textvariable=self.vars["grid_w"], width=5).pack(
            side=tk.LEFT
        )
        ttk.Label(grid_frame, text="x").pack(side=tk.LEFT, padx=2)
        ttk.Entry(grid_frame, textvariable=self.vars["grid_h"], width=5).pack(
            side=tk.LEFT
        )

        # Gap
        gap_frame = ttk.Frame(layout_frame)
        gap_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(gap_frame, text="Gap (X, Y)", width=15).pack(side=tk.LEFT)

        self.vars["gap_x"] = tk.DoubleVar(value=layout.gap_x)
        self.vars["gap_y"] = tk.DoubleVar(value=layout.gap_y)
        self.vars["gap_x"].trace_add("write", self._on_change)
        self.vars["gap_y"].trace_add("write", self._on_change)

        ttk.Entry(gap_frame, textvariable=self.vars["gap_x"], width=5).pack(
            side=tk.LEFT
        )
        ttk.Label(gap_frame, text=",").pack(side=tk.LEFT, padx=2)
        ttk.Entry(gap_frame, textvariable=self.vars["gap_y"], width=5).pack(
            side=tk.LEFT
        )

        # Margins
        margin_frame = ttk.Frame(layout_frame)
        margin_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(margin_frame, text="Margins (TRBL)", width=15).pack(side=tk.LEFT)

        self.vars["margin_t"] = tk.DoubleVar(value=layout.margin_top)
        self.vars["margin_r"] = tk.DoubleVar(value=layout.margin_right)
        self.vars["margin_b"] = tk.DoubleVar(value=layout.margin_bottom)
        self.vars["margin_l"] = tk.DoubleVar(value=layout.margin_left)

        for v in [
            self.vars["margin_t"],
            self.vars["margin_r"],
            self.vars["margin_b"],
            self.vars["margin_l"],
        ]:
            v.trace_add("write", self._on_change)
            ttk.Entry(margin_frame, textvariable=v, width=5).pack(side=tk.LEFT, padx=1)

    def _build_text_elements(self):
        if not self.spec.texts:
            return

        self._add_separator()
        text_header = ttk.Label(
            self.parent, text="Text Elements", style="Header.TLabel"
        )
        text_header.pack(fill=tk.X, padx=15, pady=(10, 5))

        for i, text_item in enumerate(self.spec.texts):
            frame = ttk.LabelFrame(self.parent, text=f"Element #{i + 1}")
            frame.pack(fill=tk.X, padx=15, pady=5)

            # Template
            t_frame = ttk.Frame(frame)
            t_frame.pack(fill=tk.X, pady=5)
            ttk.Label(t_frame, text="Template", width=10).pack(side=tk.LEFT)
            self.vars[f"text_{i}_template"] = tk.StringVar(value=text_item.template)
            self.vars[f"text_{i}_template"].trace_add("write", self._on_change)
            ttk.Entry(t_frame, textvariable=self.vars[f"text_{i}_template"]).pack(
                side=tk.LEFT, fill=tk.X, expand=True
            )

            # Position & Size
            ps_frame = ttk.Frame(frame)
            ps_frame.pack(fill=tk.X, pady=5)

            ttk.Label(ps_frame, text="Pos (x,y)", width=10).pack(side=tk.LEFT)
            self.vars[f"text_{i}_x"] = tk.DoubleVar(value=text_item.position[0])
            self.vars[f"text_{i}_y"] = tk.DoubleVar(value=text_item.position[1])
            self.vars[f"text_{i}_x"].trace_add("write", self._on_change)
            self.vars[f"text_{i}_y"].trace_add("write", self._on_change)

            ttk.Entry(ps_frame, textvariable=self.vars[f"text_{i}_x"], width=6).pack(
                side=tk.LEFT
            )
            ttk.Label(ps_frame, text=",").pack(side=tk.LEFT)
            ttk.Entry(ps_frame, textvariable=self.vars[f"text_{i}_y"], width=6).pack(
                side=tk.LEFT
            )

            ttk.Label(ps_frame, text="Size").pack(side=tk.LEFT, padx=(10, 2))
            self.vars[f"text_{i}_size"] = tk.DoubleVar(value=text_item.size)
            self.vars[f"text_{i}_size"].trace_add("write", self._on_change)
            ttk.Entry(ps_frame, textvariable=self.vars[f"text_{i}_size"], width=5).pack(
                side=tk.LEFT
            )

            # Color
            c_frame = ttk.Frame(frame)
            c_frame.pack(fill=tk.X, pady=5)
            ttk.Label(c_frame, text="Color", width=10).pack(side=tk.LEFT)
            self.vars[f"text_{i}_color"] = tk.StringVar(value=str(text_item.color))
            self.vars[f"text_{i}_color"].trace_add("write", self._on_change)
            ttk.Entry(c_frame, textvariable=self.vars[f"text_{i}_color"]).pack(
                side=tk.LEFT, fill=tk.X, expand=True
            )

    def _build_parameters(self):
        if not self.spec.params:
            return

        has_params_header = False
        for i, param in enumerate(self.spec.params):
            # Only support IntRangeParam (has min/max) for now in GUI
            if hasattr(param, "min") and hasattr(param, "max"):
                if not has_params_header:
                    self._add_separator()
                    p_header = ttk.Label(
                        self.parent,
                        text="Parameters",
                        style="Header.TLabel",
                    )
                    p_header.pack(fill=tk.X, padx=15, pady=(10, 5))
                    has_params_header = True

                frame = ttk.LabelFrame(self.parent, text=f"Variable: ${param.name}")
                frame.pack(fill=tk.X, padx=15, pady=5)

                p_frame = ttk.Frame(frame)
                p_frame.pack(fill=tk.X, pady=5)

                ttk.Label(p_frame, text="Range Min").pack(side=tk.LEFT)
                self.vars[f"param_{i}_min"] = tk.IntVar(value=param.min)
                self.vars[f"param_{i}_min"].trace_add("write", self._on_change)
                ttk.Entry(
                    p_frame, textvariable=self.vars[f"param_{i}_min"], width=8
                ).pack(side=tk.LEFT, padx=(5, 15))

                ttk.Label(p_frame, text="Range Max").pack(side=tk.LEFT)
                self.vars[f"param_{i}_max"] = tk.IntVar(value=param.max)
                self.vars[f"param_{i}_max"].trace_add("write", self._on_change)
                ttk.Entry(
                    p_frame, textvariable=self.vars[f"param_{i}_max"], width=8
                ).pack(side=tk.LEFT, padx=5)
