import threading
import tkinter as tk
import tomllib
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import tomli_w
from PIL import Image, ImageTk

from serial_stamp.engine import Engine
from serial_stamp.models import Spec


class TicketGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SerialStamp")
        self.geometry("1000x700")

        # State
        self.current_spec_path: Optional[Path] = None
        self.current_spec: Optional[Spec] = None
        self.output_path: Optional[Path] = None
        self.tk_preview_image: Optional[ImageTk.PhotoImage] = None
        self._debounce_timer: Optional[str] = None
        self.last_mtime: float = 0.0
        self._polling = False

        # UI Setup
        self._setup_menu()
        self._setup_layout()

    def _setup_layout(self):
        # Main Container
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left Panel (Config)
        self.left_frame = ttk.Frame(main_paned, width=400)
        main_paned.add(self.left_frame, weight=1)

        self._setup_config_panel()

        # Right Panel (Preview)
        self.right_frame = ttk.Frame(main_paned)
        main_paned.add(self.right_frame, weight=2)

        self._setup_preview_panel()

        # Bottom Bar (Status & Actions)
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        self._setup_bottom_bar()

    def _setup_config_panel(self):
        # Create a canvas + scrollbar for scrolling the form
        canvas = tk.Canvas(self.left_frame)
        scrollbar = ttk.Scrollbar(
            self.left_frame, orient="vertical", command=canvas.yview
        )
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Placeholder content
        ttk.Label(
            self.scrollable_frame, text="Configuration", font=("Arial", 14, "bold")
        ).pack(pady=10, anchor="w", padx=10)
        ttk.Label(
            self.scrollable_frame,
            text="(Form fields will appear here after loading a config)",
            font=("Arial", 10, "italic"),
        ).pack(pady=5, anchor="w", padx=10)

    def _setup_preview_panel(self):
        ttk.Label(self.right_frame, text="Preview", font=("Arial", 14, "bold")).pack(
            pady=10
        )

        self.preview_canvas = tk.Canvas(self.right_frame, bg="gray")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Placeholder text in canvas
        self.preview_text = self.preview_canvas.create_text(
            200, 200, text="No Preview Available", fill="white", font=("Arial", 12)
        )

        # Handle resize centering
        self.preview_canvas.bind("<Configure>", self._on_preview_resize)

    def _on_preview_resize(self, event):
        # Keep the text centered
        if hasattr(self, "preview_text"):
            self.preview_canvas.coords(
                self.preview_text, event.width / 2, event.height / 2
            )
        if self.tk_preview_image:
            self._update_preview()

    def _setup_bottom_bar(self):
        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.bottom_frame, textvariable=self.status_var).pack(
            side=tk.LEFT, padx=5
        )

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.bottom_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Buttons
        ttk.Button(
            self.bottom_frame, text="Load Config", command=self.load_config
        ).pack(side=tk.RIGHT, padx=5)
        self.generate_btn = ttk.Button(
            self.bottom_frame,
            text="Generate PDF",
            command=self.generate_pdf,
            state=tk.DISABLED,
        )
        self.generate_btn.pack(side=tk.RIGHT, padx=5)

    def _setup_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Config...", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def load_config(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("SerialStamp files", "*.stamp"), ("TOML config", "*.toml")]
        )
        if file_path:
            self.current_spec_path = Path(file_path)
            self.status_var.set(f"Loaded: {self.current_spec_path.name}")

            try:
                self._load_spec_from_file()
                self.generate_btn.config(state=tk.NORMAL)

                if not self._polling:
                    self._polling = True
                    self._poll_file_changes()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")

    def _load_spec_from_file(self):
        if not self.current_spec_path:
            return

        with open(self.current_spec_path, "rb") as f:
            data = tomllib.load(f)

        self.current_spec = Spec(**data)
        self.last_mtime = self.current_spec_path.stat().st_mtime

        self._populate_form()
        self._update_preview()

    def _poll_file_changes(self):
        if self.current_spec_path and self.current_spec_path.exists():
            try:
                current_mtime = self.current_spec_path.stat().st_mtime
                if current_mtime > self.last_mtime:
                    print("External change detected, reloading...")
                    self._load_spec_from_file()
                    self.status_var.set("Reloaded from disk")
            except OSError:
                pass

        self.after(1000, self._poll_file_changes)

    def _populate_form(self):
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.current_spec:
            return

        # Helper for sections
        def add_section_label(text):
            ttk.Label(
                self.scrollable_frame, text=text, font=("Arial", 11, "bold")
            ).pack(pady=(15, 5), anchor="w", padx=5)

        self.vars = {}  # Store TK vars

        def on_change(*args):
            self._schedule_update()

        # --- General ---
        add_section_label("General Settings")

        # Source Image
        self.vars["source_image"] = tk.StringVar(value=self.current_spec.source_image)
        self.vars["source_image"].trace_add("write", on_change)

        f = ttk.Frame(self.scrollable_frame)
        f.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(f, text="Source Image", width=15).pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=self.vars["source_image"]).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(f, text="...", width=3, command=self._browse_source_image).pack(
            side=tk.LEFT, padx=5
        )

        # Stack Size
        self.vars["stack_size"] = tk.IntVar(value=self.current_spec.stack_size)
        self.vars["stack_size"].trace_add("write", on_change)

        f = ttk.Frame(self.scrollable_frame)
        f.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(f, text="Stack Size", width=15).pack(side=tk.LEFT)
        ttk.Entry(f, textvariable=self.vars["stack_size"]).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )

        # --- Layout ---
        add_section_label("Layout")

        # Grid Size
        layout = self.current_spec.layout

        grid_frame = ttk.Frame(self.scrollable_frame)
        grid_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(grid_frame, text="Grid Size (WxH)", width=15).pack(side=tk.LEFT)

        self.vars["grid_w"] = tk.IntVar(value=layout.grid_size[0])
        self.vars["grid_h"] = tk.IntVar(value=layout.grid_size[1])
        self.vars["grid_w"].trace_add("write", on_change)
        self.vars["grid_h"].trace_add("write", on_change)

        ttk.Entry(grid_frame, textvariable=self.vars["grid_w"], width=5).pack(
            side=tk.LEFT
        )
        ttk.Label(grid_frame, text="x").pack(side=tk.LEFT, padx=2)
        ttk.Entry(grid_frame, textvariable=self.vars["grid_h"], width=5).pack(
            side=tk.LEFT
        )

        # Gap
        gap_frame = ttk.Frame(self.scrollable_frame)
        gap_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(gap_frame, text="Gap (X, Y)", width=15).pack(side=tk.LEFT)

        self.vars["gap_x"] = tk.DoubleVar(value=layout.gap_x)
        self.vars["gap_y"] = tk.DoubleVar(value=layout.gap_y)
        self.vars["gap_x"].trace_add("write", on_change)
        self.vars["gap_y"].trace_add("write", on_change)

        ttk.Entry(gap_frame, textvariable=self.vars["gap_x"], width=5).pack(
            side=tk.LEFT
        )
        ttk.Label(gap_frame, text=",").pack(side=tk.LEFT, padx=2)
        ttk.Entry(gap_frame, textvariable=self.vars["gap_y"], width=5).pack(
            side=tk.LEFT
        )

        # Margins
        margin_frame = ttk.Frame(self.scrollable_frame)
        margin_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(margin_frame, text="Margins (T,R,B,L)", width=15).pack(side=tk.LEFT)

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
            v.trace_add("write", on_change)
            ttk.Entry(margin_frame, textvariable=v, width=5).pack(side=tk.LEFT, padx=1)

        # --- Texts ---
        if self.current_spec.texts:
            add_section_label("Texts")
            for i, text_item in enumerate(self.current_spec.texts):
                frame = ttk.LabelFrame(self.scrollable_frame, text=f"Text #{i + 1}")
                frame.pack(fill=tk.X, padx=5, pady=5)

                # Template
                t_frame = ttk.Frame(frame)
                t_frame.pack(fill=tk.X, pady=2)
                ttk.Label(t_frame, text="Template", width=10).pack(side=tk.LEFT)
                self.vars[f"text_{i}_template"] = tk.StringVar(value=text_item.template)
                self.vars[f"text_{i}_template"].trace_add("write", on_change)
                ttk.Entry(t_frame, textvariable=self.vars[f"text_{i}_template"]).pack(
                    side=tk.LEFT, fill=tk.X, expand=True
                )

                # Position & Size
                ps_frame = ttk.Frame(frame)
                ps_frame.pack(fill=tk.X, pady=2)

                ttk.Label(ps_frame, text="Pos (x,y)", width=10).pack(side=tk.LEFT)
                self.vars[f"text_{i}_x"] = tk.DoubleVar(value=text_item.position[0])
                self.vars[f"text_{i}_y"] = tk.DoubleVar(value=text_item.position[1])
                self.vars[f"text_{i}_x"].trace_add("write", on_change)
                self.vars[f"text_{i}_y"].trace_add("write", on_change)

                ttk.Entry(
                    ps_frame, textvariable=self.vars[f"text_{i}_x"], width=6
                ).pack(side=tk.LEFT)
                ttk.Label(ps_frame, text=",").pack(side=tk.LEFT)
                ttk.Entry(
                    ps_frame, textvariable=self.vars[f"text_{i}_y"], width=6
                ).pack(side=tk.LEFT)

                ttk.Label(ps_frame, text="Size").pack(side=tk.LEFT, padx=(10, 2))
                self.vars[f"text_{i}_size"] = tk.DoubleVar(value=text_item.size)
                self.vars[f"text_{i}_size"].trace_add("write", on_change)
                ttk.Entry(
                    ps_frame, textvariable=self.vars[f"text_{i}_size"], width=5
                ).pack(side=tk.LEFT)

                # Color
                c_frame = ttk.Frame(frame)
                c_frame.pack(fill=tk.X, pady=2)
                ttk.Label(c_frame, text="Color", width=10).pack(side=tk.LEFT)
                self.vars[f"text_{i}_color"] = tk.StringVar(value=str(text_item.color))
                self.vars[f"text_{i}_color"].trace_add("write", on_change)
                ttk.Entry(c_frame, textvariable=self.vars[f"text_{i}_color"]).pack(
                    side=tk.LEFT, fill=tk.X, expand=True
                )

        # --- Params ---
        if self.current_spec.params:
            has_params_header = False
            for i, param in enumerate(self.current_spec.params):
                # Only support IntRangeParam (has min/max)
                if hasattr(param, "min") and hasattr(param, "max"):
                    if not has_params_header:
                        add_section_label("Parameters")
                        has_params_header = True

                    frame = ttk.LabelFrame(
                        self.scrollable_frame, text=f"Param: {param.name}"
                    )
                    frame.pack(fill=tk.X, padx=5, pady=5)

                    p_frame = ttk.Frame(frame)
                    p_frame.pack(fill=tk.X, pady=2)

                    ttk.Label(p_frame, text="Min").pack(side=tk.LEFT)
                    self.vars[f"param_{i}_min"] = tk.IntVar(value=param.min)
                    self.vars[f"param_{i}_min"].trace_add("write", on_change)
                    ttk.Entry(
                        p_frame, textvariable=self.vars[f"param_{i}_min"], width=8
                    ).pack(side=tk.LEFT, padx=5)

                    ttk.Label(p_frame, text="Max").pack(side=tk.LEFT)
                    self.vars[f"param_{i}_max"] = tk.IntVar(value=param.max)
                    self.vars[f"param_{i}_max"].trace_add("write", on_change)
                    ttk.Entry(
                        p_frame, textvariable=self.vars[f"param_{i}_max"], width=8
                    ).pack(side=tk.LEFT, padx=5)

    def _browse_source_image(self):
        initial_dir = self.current_spec_path.parent if self.current_spec_path else None
        filename = filedialog.askopenfilename(
            initialdir=initial_dir, filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )
        if filename:
            try:
                p = Path(filename)
                if self.current_spec_path:
                    rel = p.relative_to(self.current_spec_path.parent)
                    self.vars["source_image"].set(str(rel))
                else:
                    self.vars["source_image"].set(filename)
            except (ValueError, AttributeError):
                self.vars["source_image"].set(filename)

    def _schedule_update(self):
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(500, self._update_preview_from_form)

    def _update_preview_from_form(self):
        self._debounce_timer = None
        if not self.current_spec:
            return

        try:
            # Update Spec object from vars
            self.current_spec.stack_size = self.vars["stack_size"].get()
            self.current_spec.source_image = self.vars["source_image"].get()

            # Layout
            layout = self.current_spec.layout
            layout.grid_size = (self.vars["grid_w"].get(), self.vars["grid_h"].get())
            layout.gap = (self.vars["gap_x"].get(), self.vars["gap_y"].get())
            layout.margin = (
                self.vars["margin_t"].get(),
                self.vars["margin_r"].get(),
                self.vars["margin_b"].get(),
                self.vars["margin_l"].get(),
            )

            # Update Texts
            if self.current_spec.texts:
                for i, text_item in enumerate(self.current_spec.texts):
                    if f"text_{i}_template" in self.vars:
                        text_item.template = self.vars[f"text_{i}_template"].get()
                        text_item.position = (
                            self.vars[f"text_{i}_x"].get(),
                            self.vars[f"text_{i}_y"].get(),
                        )
                        text_item.size = self.vars[f"text_{i}_size"].get()

                        # Invalidate cached font property so it reloads with new size
                        if "font" in text_item.__dict__:
                            del text_item.__dict__["font"]

                        # Handle color (literal eval if looks like tuple)
                        c_str = self.vars[f"text_{i}_color"].get()
                        if c_str.startswith("(") and c_str.endswith(")"):
                            try:
                                import ast

                                text_item.color = ast.literal_eval(c_str)
                            except (ValueError, SyntaxError):
                                text_item.color = c_str
                        else:
                            text_item.color = c_str

            # Update Params
            if self.current_spec.params:
                for i, param in enumerate(self.current_spec.params):
                    if hasattr(param, "min") and hasattr(param, "max"):
                        if f"param_{i}_min" in self.vars:
                            param.min = self.vars[f"param_{i}_min"].get()
                        if f"param_{i}_max" in self.vars:
                            param.max = self.vars[f"param_{i}_max"].get()

            self._update_preview()
            self._save_config()
            self.status_var.set("Saved & Preview Updated")
        except tk.TclError:
            # Occurs when inputs are empty/invalid (e.g. integer fields)
            pass
        except Exception as e:
            # Fail silently to console for other errors to avoid popup spam
            print(f"Update error: {e}")

    def _save_config(self):
        if not self.current_spec or not self.current_spec_path:
            return

        try:
            data = self.current_spec.model_dump(by_alias=True, exclude_none=True)
            with open(self.current_spec_path, "wb") as f:
                tomli_w.dump(data, f)

            # Update last_mtime so we don't reload our own save
            self.last_mtime = self.current_spec_path.stat().st_mtime
        except Exception as e:
            print(f"Autosave failed: {e}")
            self.status_var.set("Autosave failed!")

    def _update_preview(self):
        if not self.current_spec or not self.current_spec_path:
            return

        try:
            # Resolve image path
            img_path_str = self.current_spec.source_image
            img_path = Path(img_path_str)
            if not img_path.is_absolute():
                img_path = self.current_spec_path.parent / img_path

            if not img_path.exists():
                self.preview_canvas.delete("all")
                self.preview_text = self.preview_canvas.create_text(
                    200,
                    200,
                    text=f"Image not found:\n{img_path}",
                    fill="red",
                    justify="center",
                )
                return

            with Image.open(img_path) as source_image:
                # We need a dummy output path
                engine = Engine(self.current_spec, Path("preview.pdf"), source_image)
                preview_img = engine.generate_preview()

                # Resize to fit canvas
                c_w = self.preview_canvas.winfo_width()
                c_h = self.preview_canvas.winfo_height()

                if c_w < 10 or c_h < 10:
                    c_w, c_h = 400, 600  # Default if not mapped yet

                img_w, img_h = preview_img.size
                ratio = min(c_w / img_w, c_h / img_h)
                new_size = (int(img_w * ratio), int(img_h * ratio))

                if new_size[0] > 0 and new_size[1] > 0:
                    resized = preview_img.resize(new_size, Image.Resampling.LANCZOS)
                    self.tk_preview_image = ImageTk.PhotoImage(
                        resized
                    )  # Keep reference!

                    self.preview_canvas.delete("all")
                    # Center it
                    x = c_w / 2
                    y = c_h / 2
                    self.preview_canvas.create_image(x, y, image=self.tk_preview_image)

        except Exception as e:
            print(f"Preview error: {e}")
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                200,
                200,
                text=f"Preview Error:\n{e}",
                fill="red",
                width=300,
            )

    def generate_pdf(self):
        if not self.current_spec or not self.current_spec_path:
            return

        output_filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{self.current_spec_path.stem}-out.pdf",
        )

        if not output_filename:
            return

        self.output_path = Path(output_filename)
        self.generate_btn.config(state=tk.DISABLED)
        self.status_var.set("Generating...")
        self.progress_var.set(0)

        # Capture state for thread
        spec = self.current_spec
        spec_path = self.current_spec_path
        output_path = self.output_path

        # Run in thread
        thread = threading.Thread(
            target=self._run_generation, args=(spec, spec_path, output_path)
        )
        thread.daemon = True
        thread.start()

    def _run_generation(self, spec: Spec, spec_path: Path, output_path: Path):
        try:
            # Resolve image path again for the engine
            img_path_str = spec.source_image
            img_path = Path(img_path_str)
            if not img_path.is_absolute():
                img_path = spec_path.parent / img_path

            with Image.open(img_path) as source_image:
                engine = Engine(spec, output_path, source_image)
                engine.generate(progress_callback=self._update_progress_threadsafe)

            self.after(0, self._generation_complete, True, None)
        except Exception as e:
            self.after(0, self._generation_complete, False, str(e))

    def _update_progress_threadsafe(self, current, total):
        self.after(0, self._update_progress, current, total)

    def _update_progress(self, current, total):
        if total > 0:
            percent = (current / total) * 100
            self.progress_var.set(percent)
            self.status_var.set(f"Generating: Page {current}/{total}")

    def _generation_complete(self, success, error_msg):
        self.generate_btn.config(state=tk.NORMAL)
        if success:
            self.status_var.set("Generation Complete!")
            self.progress_var.set(100)
            messagebox.showinfo("Success", f"PDF saved to:\n{self.output_path}")
        else:
            self.status_var.set("Error during generation")
            messagebox.showerror("Error", f"Generation failed:\n{error_msg}")


def main():
    app = TicketGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
