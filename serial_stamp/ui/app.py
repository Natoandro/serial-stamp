import queue
import tempfile
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
from serial_stamp.project import Project, init_project, pack_project
from serial_stamp.ui.forms import FormBuilder
from serial_stamp.ui.panels import BottomBar, ConfigPanel, PreviewPanel


class TicketGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SerialStamp")
        self.geometry("1000x700")

        # Style Configuration
        self._setup_style()

        # State
        self.project: Optional[Project] = None
        self.current_spec: Optional[Spec] = None
        self.output_path: Optional[Path] = None
        self._debounce_timer: Optional[str] = None
        self.last_mtime: float = 0.0
        self._polling = False
        self.msg_queue: queue.Queue = queue.Queue()

        # UI Components
        self.config_panel: ConfigPanel
        self.preview_panel: PreviewPanel
        self.bottom_bar: BottomBar

        # UI Setup
        self._setup_menu()
        self._setup_layout()

        self._check_queue()

        # Delay initial preview rendering until the Tk event loop has started and
        # widgets are mapped.
        self.after(0, self._update_preview)

    def _check_queue(self):
        try:
            while True:
                func, args = self.msg_queue.get_nowait()
                func(*args)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._check_queue)

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass  # Fallback to default if unavailable

        # Colors
        bg_color = "#f0f0f0"
        self.configure(bg=bg_color)

        # Fonts
        header_font = ("Segoe UI", 12, "bold")
        normal_font = ("Segoe UI", 10)

        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, font=normal_font)
        style.configure("Header.TLabel", font=header_font, foreground="#333")
        style.configure(
            "TButton", font=normal_font, padding=6, borderwidth=0, focuscolor="none"
        )
        style.map(
            "TButton",
            background=[("active", "#e1e1e1"), ("!disabled", "#ffffff")],
            foreground=[("!disabled", "#333")],
        )
        style.configure("TLabelframe", background=bg_color, padding=10)
        style.configure("TLabelframe.Label", background=bg_color, font=header_font)
        style.configure("TEntry", padding=4)
        style.configure("Horizontal.TProgressbar", background="#4CAF50")

    def _setup_layout(self):
        # Main Container with padding
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel (Config) - Increased initial width
        self.left_frame = ttk.Frame(main_paned, width=450)
        main_paned.add(self.left_frame, weight=1)

        self.config_panel = ConfigPanel(self.left_frame)
        self.config_panel.pack(fill=tk.BOTH, expand=True)

        # Right Panel (Preview)
        self.right_frame = ttk.Frame(main_paned)
        main_paned.add(self.right_frame, weight=3)

        self.preview_panel = PreviewPanel(
            self.right_frame, on_resize_callback=self._on_preview_resize
        )
        self.preview_panel.pack(fill=tk.BOTH, expand=True)

        # Bottom Bar (Status & Actions)
        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))

        self.bottom_bar = BottomBar(
            self.bottom_frame,
            on_load=self.load_config,
            on_generate=self.generate_pdf,
        )
        self.bottom_bar.pack(fill=tk.X, expand=True)

    def _on_preview_resize(self, event):
        # Trigger update if we have a valid image to resize
        if self.preview_panel.tk_preview_image:
            self._update_preview()

    def _setup_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project...", command=self.new_project)
        file_menu.add_command(label="Open Project...", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def new_project(self):
        file_path = filedialog.asksaveasfilename(
            title="Create New Project",
            defaultextension=".stamp",
            filetypes=[("SerialStamp Project", "*.stamp")],
        )
        if file_path:
            try:
                # cleanup current
                if self.project:
                    self.project.__exit__(None, None, None)

                # 1. Create temporary directory structure
                with tempfile.TemporaryDirectory() as tmp:
                    # init_project creates assets/ and spec.toml in 'tmp'
                    init_project(tmp)
                    # 2. Pack it to the destination .stamp file
                    pack_project(tmp, file_path)

                # 3. Load the new project
                self.project = Project(file_path)
                self.project.__enter__()
                self._load_spec_from_project()
                self.bottom_bar.generate_btn.config(state=tk.NORMAL)
                self.bottom_bar.status_var.set(f"Created: {Path(file_path).name}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to create project: {e}")

    def load_config(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("SerialStamp files", "*.stamp"), ("TOML config", "*.toml")]
        )
        if file_path:
            self.bottom_bar.status_var.set(f"Loaded: {Path(file_path).name}")

            try:
                # Cleanup previous project if exists
                if self.project:
                    self.project.__exit__(None, None, None)

                # Initialize new project
                self.project = Project(file_path)
                self.project.__enter__()  # Enter context manually to extract files

                self._load_spec_from_project()

                self.bottom_bar.generate_btn.config(state=tk.NORMAL)

                if not self._polling:
                    self._polling = True
                    self._poll_file_changes()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")

    def _load_spec_from_project(self):
        if not self.project:
            return

        with open(self.project.spec_path, "rb") as f:
            data = tomllib.load(f)

        self.current_spec = Spec(**data)
        # Track mtime of the ROOT path (the zip or the toml), not the extracted spec
        if self.project.root_path.exists():
            self.last_mtime = self.project.root_path.stat().st_mtime

        self._populate_form()

        # Delay preview update to run after the current event cycle. This ensures
        # the preview canvas has a stable size and the window is mapped.
        self.after(0, self._update_preview)

    def _poll_file_changes(self):
        if self.project and self.project.root_path.exists():
            try:
                current_mtime = self.project.root_path.stat().st_mtime
                if current_mtime > self.last_mtime:
                    print("External change detected, reloading...")
                    self.project.__exit__(None, None, None)
                    self.project.__enter__()

                    self._load_spec_from_project()
                    self.bottom_bar.status_var.set("Reloaded from disk")
            except OSError:
                pass

        self.after(1000, self._poll_file_changes)

    def _populate_form(self):
        # Clear existing
        self.config_panel.clear()

        if not self.current_spec:
            return

        builder = FormBuilder(
            self.config_panel.scrollable_frame,
            self.current_spec,
            self._schedule_update,
            self._browse_source_image,
        )
        self.vars = builder.build()

    def _browse_source_image(self):
        initial_dir = self.project.root_path.parent if self.project else None
        filename = filedialog.askopenfilename(
            initialdir=initial_dir, filetypes=[("Images", "*.jpg *.jpeg *.png")]
        )
        if filename:
            if self.project:
                try:
                    # Import asset into project
                    rel_path = self.project.import_asset(filename)
                    self.vars["source_image"].set(rel_path)
                except Exception as e:
                    print(f"Failed to import asset: {e}")
                    self.vars["source_image"].set(filename)
            else:
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
                        text_item.size = int(self.vars[f"text_{i}_size"].get())

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
            self.bottom_bar.status_var.set("Saved & Preview Updated")
        except tk.TclError:
            # Occurs when inputs are empty/invalid (e.g. integer fields)
            pass
        except Exception as e:
            # Fail silently to console for other errors to avoid popup spam
            print(f"Update error: {e}")

    def _save_config(self):
        if not self.current_spec or not self.project:
            return

        try:
            # 1. Write the Spec TOML to the working directory (temp or real)
            data = self.current_spec.model_dump(by_alias=True, exclude_none=True)
            with open(self.project.spec_path, "wb") as f:
                tomli_w.dump(data, f)

            # 2. Persist changes (re-pack zip if needed)
            self.project.save()

            # Update last_mtime so we don't reload our own save
            if self.project.root_path.exists():
                self.last_mtime = self.project.root_path.stat().st_mtime
        except Exception as e:
            print(f"Autosave failed: {e}")
            self.bottom_bar.status_var.set("Autosave failed!")

    def _update_preview(self):
        if not self.current_spec or not self.project:
            return

        try:
            # Resolve image path relative to project working dir
            img_path_str = self.current_spec.source_image
            img_path = self.project.work_dir / img_path_str

            if not img_path.exists() or img_path.is_dir():
                self.preview_panel.show_message(
                    f"Image not found:\n{img_path}", color="red"
                )
                return

            with Image.open(img_path) as source_image:
                # We need a dummy output path
                engine = Engine(self.current_spec, Path("preview.pdf"), source_image)
                preview_img = engine.generate_preview()

                # Resize to fit canvas
                c_w, c_h = self.preview_panel.get_canvas_size()

                if c_w < 10 or c_h < 10:
                    c_w, c_h = 400, 600  # Default if not mapped yet

                img_w, img_h = preview_img.size
                ratio = min(c_w / img_w, c_h / img_h)
                new_size = (int(img_w * ratio), int(img_h * ratio))

                if new_size[0] > 0 and new_size[1] > 0:
                    resized = preview_img.resize(new_size, Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(resized)
                    self.preview_panel.show_image(tk_img)
                else:
                    pass

        except Exception as e:
            self.preview_panel.show_message(f"Preview Error:\n{e}", color="red")

    def generate_pdf(self):
        if not self.current_spec or not self.project:
            return

        output_filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{self.project.root_path.stem}-out.pdf",
        )

        if not output_filename:
            return

        self.output_path = Path(output_filename)
        self.bottom_bar.generate_btn.config(state=tk.DISABLED)
        self.bottom_bar.status_var.set("Generating...")
        self.bottom_bar.progress_var.set(0)

        # Capture state for thread
        # Clone spec to avoid race conditions if UI modifies it during generation
        spec = self.current_spec.model_copy(deep=True)
        # We pass the WORKING directory path, so engine can find assets
        work_dir = self.project.work_dir
        output_path = self.output_path

        # Run in thread
        thread = threading.Thread(
            target=self._run_generation, args=(spec, work_dir, output_path)
        )
        thread.daemon = True
        thread.start()

    def _run_generation(self, spec: Spec, work_dir: Path, output_path: Path):
        try:
            # Resolve image path again for the engine
            img_path_str = spec.source_image
            img_path = work_dir / img_path_str

            with Image.open(img_path) as source_image:
                engine = Engine(spec, output_path, source_image)
                engine.generate(progress_callback=self._update_progress_threadsafe)

            self.msg_queue.put((self._generation_complete, (True, None)))
        except Exception as e:
            self.msg_queue.put((self._generation_complete, (False, str(e))))

    def _update_progress_threadsafe(self, current, total):
        self.msg_queue.put((self._update_progress, (current, total)))

    def _update_progress(self, current, total):
        if total > 0:
            percent = (current / total) * 100
            self.bottom_bar.progress_var.set(percent)
            self.bottom_bar.status_var.set(f"Generating: Page {current}/{total}")

    def _generation_complete(self, success, error_msg):
        self.bottom_bar.generate_btn.config(state=tk.NORMAL)
        if success:
            self.bottom_bar.status_var.set("Generation Complete!")
            self.bottom_bar.progress_var.set(100)
            messagebox.showinfo("Success", f"PDF saved to:\n{self.output_path}")
        else:
            self.bottom_bar.status_var.set("Error during generation")
            messagebox.showerror("Error", f"Generation failed:\n{error_msg}")
