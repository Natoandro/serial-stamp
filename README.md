# SerialStamp

**SerialStamp** is a tool for adding iterative numbers, serial codes, or dynamic text to images and stacking them into printable PDF pages. It is ideal for generating tickets, vouchers, invitations, and other serialized documents.

## Features

- **Dynamic Text Replacement**: Use variables like `$no` in your text templates to insert serial numbers.
- **Batch Generation**: Generate thousands of unique images in seconds.
- **PDF Stacking**: Automatically arranges generated images onto pages (grids) and saves them as a multi-page PDF.
- **Graphical User Interface (GUI)**:
  - Live preview of your layout.
  - Form-based editing for text, positions, and parameters.
  - Automatic reload on external config changes.
  - Autosave functionality.
- **Configuration**: Uses simple TOML files (`.stamp` or `.toml`) to define layouts and parameters.

## Installation

Ensure you have [uv](https://docs.astral.sh/uv/) installed.

```bash
# Clone the repository
git clone https://github.com/Natoandro/serial-stamp.git
cd serial-stamp

# Install dependencies
uv sync
```

## Development

### Setup

1.  Install dependencies (including dev tools):
    ```bash
    uv sync
    ```

2.  Install git hooks:
    ```bash
    uv run pre-commit install
    ```

### Code Quality

-   **Linting/Formatting**: `uv run ruff check .` / `uv run ruff format .`
-   **Type Checking**: `uv run mypy .`

## Usage

### Graphical Interface (Recommended)

Run the GUI to visually edit your configuration and generate PDFs.

```bash
uv run serial-stamp-gui
```

1.  **Load Config**: Open an existing `.stamp` or `.toml` file (examples included in the repo).
2.  **Edit**: Modify the source image, grid layout, margins, texts, and parameter ranges in the form.
3.  **Preview**: See the changes in real-time in the preview pane.
4.  **Generate**: Click "Generate PDF" to create the final output.

### Command Line Interface

**Initialize a New Project**
Create a folder structure with a template spec:
```bash
uv run serial-stamp init my_project
```

**Pack a Project**
Bundle a folder into a portable `.stamp` file:
```bash
uv run serial-stamp pack my_project -o project.stamp
```

**Generate PDF**
Generate output from a `.stamp` file, `.toml` config, or folder:
```bash
uv run serial-stamp generate project.stamp -o output.pdf
```

## Configuration Format

The configuration is defined in a `spec.toml` file using the TOML format. This file resides at the root of your project directory or inside a packed `.stamp` archive.

### Example (`spec.toml`)

```toml
stack-size = 5
source-image = "images/ticket.jpg"

[layout]
grid-size = [2, 3]  # 2 columns, 3 rows
gap = [50, 5]       # Gap between items (x, y)
margin = 10         # Margin around the page

[[texts]]
template = "N° $no"
position = [1120, 537]
size = 24
ttf = "fonts/Roboto-Medium.ttf"
color = "blue"

[[params]]
name = "no"
type = "int"
min = 1
max = 100
```

## Project Structure

- `serial_stamp/`: Main Python package.
  - `gui.py`: Graphical user interface.
  - `cli.py`: Command-line entry point.
  - `engine.py`: Core logic for image generation and PDF stacking.
  - `models.py`: Data models (Pydantic).
  - `project.py`: Project management (packed/unpacked modes).
- `scripts/`: Legacy scripts and utilities.
