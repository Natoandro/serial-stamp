import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional


class Project:
    def __init__(self, path: str | Path):
        self.root_path = Path(path).resolve()
        self.work_dir: Path = Path(".")
        self.is_temp: bool = False
        self._temp_dir: Optional[tempfile.TemporaryDirectory] = None
        self._spec_filename: str = "spec.toml"

    def __enter__(self):
        if self.root_path.is_file():
            if self.root_path.suffix in (".stamp", ".zip"):
                self._setup_packed()
            elif self.root_path.suffix == ".toml":
                self._setup_toml_file()
            else:
                # Fallback: check magic number or assume generic zip if valid
                if zipfile.is_zipfile(self.root_path):
                    self._setup_packed()
                else:
                    raise ValueError(f"Unsupported file type: {self.root_path}")
        elif self.root_path.is_dir():
            self._setup_directory()
        else:
            # Path doesn't exist, assume creating new via GUI loading non-existent?
            # Or CLI init? Usually we expect existing path here.
            raise FileNotFoundError(f"Project path not found: {self.root_path}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._temp_dir:
            self._temp_dir.cleanup()
            self._temp_dir = None

    def _setup_packed(self):
        self._temp_dir = tempfile.TemporaryDirectory(prefix="serial_stamp_")
        self.work_dir = Path(self._temp_dir.name)
        self.is_temp = True

        with zipfile.ZipFile(self.root_path, "r") as zf:
            zf.extractall(self.work_dir)

        # Detect spec file
        if not (self.work_dir / "spec.toml").exists():
            tomls = list(self.work_dir.glob("*.toml"))
            if tomls:
                self._spec_filename = tomls[0].name

    def _setup_toml_file(self):
        self.work_dir = self.root_path.parent
        self._spec_filename = self.root_path.name
        self.is_temp = False

    def _setup_directory(self):
        self.work_dir = self.root_path
        self.is_temp = False
        # Find spec file
        if not (self.work_dir / "spec.toml").exists():
            tomls = list(self.work_dir.glob("*.toml"))
            if tomls:
                self._spec_filename = tomls[0].name

    @property
    def spec_path(self) -> Path:
        return self.work_dir / self._spec_filename

    @property
    def assets_dir(self) -> Path:
        p = self.work_dir / "assets"
        p.mkdir(exist_ok=True)
        return p

    def import_asset(self, source_path: Path | str) -> str:
        """
        Copies external file to project assets and returns relative path string.
        """
        src = Path(source_path)
        dest = self.assets_dir / src.name

        # Avoid copying if it's the same file
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)

        # Return relative path using forward slashes for TOML compatibility
        return f"assets/{src.name}"

    def save(self):
        """
        Persists changes.
        For packed projects, re-zips the work_dir to root_path.
        For unpacked projects, this is a no-op (files modified in place).
        """
        if not self.is_temp:
            return

        # We write directly to the root_path, replacing the old zip
        with zipfile.ZipFile(self.root_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.work_dir.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.work_dir)
                    zf.write(file_path, rel_path)


def init_project(path: Path | str):
    """Creates a new project structure at the given path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    (p / "assets").mkdir(exist_ok=True)

    spec_content = """stack-size = 1
source-image = ""

[layout]
grid-size = [1, 1]
gap = 0
margin = 0

[[texts]]
template = "Sample Text"
position = [10, 10]
size = 24
color = "black"
"""
    with open(p / "spec.toml", "w") as f:
        f.write(spec_content)


def pack_project(source_dir: Path | str, output_path: Path | str):
    """Bundles a directory into a .stamp file."""
    src = Path(source_dir)
    out = Path(output_path)

    if not src.is_dir():
        raise ValueError("Source must be a directory")

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in src.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(src)
                zf.write(file_path, rel_path)
