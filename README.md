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

Ensure you have Python 3.11+ installed.

```bash
# Clone the repository
git clone <repository-url>
cd image_manip

# Install dependencies
pip install pillow pydantic tomli-w
```

## Usage

### Graphical Interface (Recommended)

Run the GUI to visually edit your configuration and generate PDFs.

```bash
python -m serial_stamp.gui
```

1.  **Load Config**: Open an existing `.stamp` or `.toml` file (examples included in the repo).
2.  **Edit**: Modify the source image, grid layout, margins, texts, and parameter ranges in the form.
3.  **Preview**: See the changes in real-time in the preview pane.
4.  **Generate**: Click "Generate PDF" to create the final output.

### Command Line Interface

You can also run the generator directly from the command line if you already have a configuration file.

```bash
python -m serial_stamp.cli config.stamp -o output.pdf
```

## Configuration Format

Configuration files use the TOML format. Save them with a `.stamp` extension.

### Example (`bka.stamp`)

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
- `scripts/`: Legacy scripts and utilities.