# SerialStamp CLI User Guide

**Temporary guide while the desktop app is under development**

This guide will help you use SerialStamp's command-line interface to generate serialized documents like tickets, vouchers, and invitations.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Commands Overview](#commands-overview)
3. [Configuration File (spec.toml)](#configuration-file-spectoml)
4. [Common Workflows](#common-workflows)
5. [Troubleshooting](#troubleshooting)
6. [Examples](#examples)

---

## Quick Start

### Prerequisites

Make sure you have [uv](https://docs.astral.sh/uv/) installed and the project dependencies synced:

```bash
cd image_manip
uv sync
```

### Basic Workflow

1. **Create a new project**:
   ```bash
   uv run serial-stamp init my_tickets
   cd my_tickets
   ```

2. **Add your source image** to the `assets/` folder:
   ```bash
   cp ~/my_ticket_background.png assets/
   ```

3. **Edit `spec.toml`** to configure your layout and text (see [Configuration](#configuration-file-spectoml))

4. **Generate a preview** to test:
   ```bash
   uv run serial-stamp preview . -o test.png
   ```

5. **Generate the final PDF**:
   ```bash
   uv run serial-stamp generate . -o output.pdf
   ```

---

## Commands Overview

### 1. `init` - Create a New Project

Creates a project folder with the required structure.

```bash
uv run serial-stamp init <path>
```

**Example**:
```bash
uv run serial-stamp init my_tickets
```

**Creates**:
```
my_tickets/
├── assets/          # Put images and fonts here
└── spec.toml        # Configuration file
```

---

### 2. `pack` - Bundle Project into .stamp File

Creates a portable `.stamp` archive (ZIP format) containing your entire project.

```bash
uv run serial-stamp pack <source_directory> -o <output.stamp>
```

**Example**:
```bash
uv run serial-stamp pack my_tickets -o tickets.stamp
```

**Benefits**:
- Share projects easily
- Archive completed projects
- Portable single-file format

---

### 3. `generate` - Create PDF Output

Generates the final multi-page PDF with all your serialized documents.

```bash
uv run serial-stamp generate <input> -o <output.pdf>
```

**Input can be**:
- Project directory: `projects/my_tickets`
- Standalone TOML file: `config.toml`
- Packed .stamp file: `project.stamp`

**Examples**:
```bash
# From project directory
uv run serial-stamp generate projects/oc-40-2 -o tickets.pdf

# From TOML file
uv run serial-stamp generate my_config.toml -o output.pdf

# From .stamp file
uv run serial-stamp pack my_tickets -o tickets.stamp
uv run serial-stamp generate tickets.stamp -o output.pdf
```

---

### 4. `preview` - Generate Test Image

Creates a preview image of a single page to verify your layout before generating the full PDF.

```bash
uv run serial-stamp preview <input> -o <output.png>
```

**Example**:
```bash
uv run serial-stamp preview . -o test.png
```

**Tip**: Use this frequently while adjusting text positions and styling!

---

## Configuration File (spec.toml)

The `spec.toml` file defines your document layout, text elements, and parameters.

### Complete Example

```toml
# How many documents to generate
# Set to 1 to generate all combinations, or a specific number to limit output
stack-size = 5

# Path to your base image (relative to project root or TOML file)
source-image = "assets/ticket_background.png"

# Page layout configuration
[layout]
grid-size = [2, 6]        # 2 columns × 6 rows = 12 tickets per page
gap = [10, 10]            # Horizontal and vertical spacing (pixels)
margin = 10               # Page margin (can also be [top, right, bottom, left])

# Text element #1
[[texts]]
template = "N° $no"                      # Use $variable for dynamic values
position = [920, 420]                    # X, Y coordinates on the image
size = 30                                # Font size in points
ttf = "assets/Roboto-Medium.ttf"         # Path to TrueType font
color = "white"                          # Color (name or RGB)

# Text element #2
[[texts]]
template = "Seat: $section-$seat"
position = [100, 50]
size = 24
ttf = "assets/Roboto-Bold.ttf"
color = [255, 0, 0]                      # RGB: red

# Parameter: serial number
[[params]]
name = "no"
type = "int"
min = 301
max = 600
leading-zeros = 3         # Pads numbers: 301, 302, ..., 600

# Parameter: section letters
[[params]]
name = "section"
type = "string"
values = ["A", "B", "C", "D"]

# Parameter: seat numbers
[[params]]
name = "seat"
type = "int"
values = [1, 2, 3, 4, 5]
```

---

### Configuration Sections Explained

#### 1. **Basic Settings**

```toml
stack-size = 5
source-image = "assets/background.png"
```

- **`stack-size`**: Number of documents to generate
  - Set to `1` to generate ALL parameter combinations
  - Set to a specific number (e.g., `50`) to limit output
- **`source-image`**: Path to your base image
  - Relative to project root for project directories
  - Relative to TOML file for standalone configs

---

#### 2. **Layout Configuration**

```toml
[layout]
grid-size = [columns, rows]
gap = spacing_value
margin = margin_value
```

**`grid-size`**: How documents are arranged per page
```toml
grid-size = [2, 3]    # 2 columns, 3 rows = 6 documents per page
grid-size = [1, 1]    # Single document per page
```

**`gap`**: Space between documents
```toml
gap = 10              # Same horizontal and vertical gap
gap = [20, 15]        # Horizontal: 20px, Vertical: 15px
```

**`margin`**: Space around page edges
```toml
margin = 10                      # All sides: 10px
margin = [10, 20]                # Vertical: 10px, Horizontal: 20px
margin = [10, 20, 15, 25]        # Top, Right, Bottom, Left
```

---

#### 3. **Text Elements**

Add as many `[[texts]]` blocks as needed. Each adds dynamic or static text to your document.

```toml
[[texts]]
template = "Ticket #$number"              # Text with variable
position = [100, 50]                      # X, Y coordinates (pixels from top-left)
size = 24                                 # Font size in points
ttf = "assets/fonts/MyFont.ttf"          # Path to font file
color = "black"                           # Color
```

**Template Variables**: Use `$variable_name` to insert dynamic values from parameters.

**Position**: `[x, y]` coordinates with origin at top-left corner of the image.

**Color Options**:
```toml
color = "red"                    # Named color
color = "black"
color = "white"
color = [255, 0, 0]             # RGB: red
color = [255, 0, 0, 200]        # RGBA with transparency
```

**Font (ttf)**:
- **Required**: Must point to an actual `.ttf` or `.otf` file
- **Common mistake**: Don't use directory paths like `ttf = "assets"`
- **Correct**: `ttf = "assets/Roboto-Medium.ttf"`
- If omitted, uses system default font

---

#### 4. **Parameters (Variables)**

Parameters define the dynamic values that change across documents.

##### **A. Integer Range**

Sequential numbers from min to max:

```toml
[[params]]
name = "ticket_no"
type = "int"
min = 1
max = 500
leading-zeros = 4        # Optional: pads to 0001, 0002, ..., 0500
```

##### **B. Integer List**

Specific integer values:

```toml
[[params]]
name = "seat"
type = "int"
values = [10, 20, 25, 30, 42]
leading-zeros = 2        # Optional: 10, 20, 25, 30, 42
```

##### **C. String List**

Text values that cycle through:

```toml
[[params]]
name = "category"
type = "string"
values = ["VIP", "Standard", "Economy"]
```

##### **D. String Array** (Advanced)

Multiple values per document:

```toml
[[params]]
name = "attendees"
type = "string[]"
length = 3
values = [
  ["Alice", "Bob", "Charlie"],
  ["David", "Eve", "Frank"],
  ["Grace", "Heidi", "Ivan"]
]

# Use in templates:
# "$attendees[0]" → First attendee
# "$attendees[1]" → Second attendee
# "$attendees[2]" → Third attendee
```

---

#### 5. **Output Settings** (Optional)

```toml
[output]
background-color = "white"           # Page background color
# or
background-color = [240, 240, 240]   # RGB gray
```

---

## Common Workflows

### Workflow 1: Creating Event Tickets

```bash
# 1. Initialize project
uv run serial-stamp init event_tickets
cd event_tickets

# 2. Copy your ticket design
cp ~/ticket_design.png assets/

# 3. Copy font (if using custom font)
cp ~/Roboto-Bold.ttf assets/

# 4. Edit spec.toml
nano spec.toml
```

**spec.toml**:
```toml
stack-size = 1
source-image = "assets/ticket_design.png"

[layout]
grid-size = [2, 5]
gap = [15, 15]
margin = 20

[[texts]]
template = "TICKET #$number"
position = [100, 50]
size = 32
ttf = "assets/Roboto-Bold.ttf"
color = "black"

[[texts]]
template = "Section: $section"
position = [100, 100]
size = 24
ttf = "assets/Roboto-Bold.ttf"
color = [0, 0, 255]

[[params]]
name = "number"
type = "int"
min = 1
max = 100
leading-zeros = 3

[[params]]
name = "section"
type = "string"
values = ["A", "B", "C", "D"]
```

```bash
# 5. Preview first
uv run serial-stamp preview . -o test.png
open test.png  # Check the result

# 6. Generate PDF
uv run serial-stamp generate . -o tickets.pdf
```

---

### Workflow 2: Using Standalone TOML File

For quick tests without full project structure:

```bash
# Create a simple TOML file next to your image
cd ~/my_images
nano quick_test.toml
```

**quick_test.toml**:
```toml
stack-size = 1
source-image = "background.png"  # In same directory

[layout]
grid-size = [1, 1]
gap = 0
margin = 0

[[texts]]
template = "Number: $n"
position = [50, 50]
size = 24
color = "black"

[[params]]
name = "n"
type = "int"
min = 1
max = 10
```

```bash
# Generate directly
uv run serial-stamp generate quick_test.toml -o output.pdf
```

---

### Workflow 3: Iterating on Design

When fine-tuning text positions:

```bash
# 1. Edit spec.toml - adjust positions
nano spec.toml

# 2. Generate preview
uv run serial-stamp preview . -o test.png

# 3. Check result
open test.png

# 4. Repeat steps 1-3 until satisfied

# 5. Generate final PDF
uv run serial-stamp generate . -o final.pdf
```

**Tip**: Keep the preview image open and just refresh after each generation!

---

### Workflow 4: Sharing Projects

```bash
# Pack your project
uv run serial-stamp pack event_tickets -o event_tickets.stamp

# Share the .stamp file
# Recipients can use it directly:
uv run serial-stamp generate event_tickets.stamp -o output.pdf
```

---

## Troubleshooting

### Error: "cannot open resource"

**Cause**: Font file path is incorrect or points to a directory.

**Solution**:
```toml
# ❌ Wrong - points to directory
ttf = "assets"

# ✅ Correct - points to actual font file
ttf = "assets/Roboto-Medium.ttf"
```

**Verify font exists**:
```bash
ls -la assets/*.ttf
```

---

### Error: "Source image not found"

**Cause**: Image path in `spec.toml` is incorrect.

**Solution**:
1. Check the path in `spec.toml`:
   ```toml
   source-image = "assets/my_image.png"
   ```

2. Verify the file exists:
   ```bash
   ls -la assets/
   ```

3. Ensure path is relative to:
   - Project root (for project directories)
   - TOML file location (for standalone .toml files)

---

### Error: "Spec file not found"

**Cause**: Running from wrong directory or spec.toml is missing.

**Solution**:
```bash
# Check current directory
ls -la

# Should see spec.toml
# If not, either:
# 1. cd to correct directory
# 2. Specify full path: uv run serial-stamp generate /path/to/project -o out.pdf
```

---

### Preview looks wrong / Text not visible

**Common issues**:

1. **Text position off-screen**: Check your `position` values
   ```bash
   # Open your source image in an image viewer
   # Note the dimensions (e.g., 800×600)
   # Ensure position values are within bounds
   ```

2. **Text color same as background**: Change color
   ```toml
   # If background is white:
   color = "black"  # Not white!
   ```

3. **Font size too small/large**: Adjust `size`
   ```toml
   size = 48  # Try larger values
   ```

---

### PDF generates but is empty/blank

**Causes**:
1. No parameters defined
2. `stack-size` doesn't match expectations

**Solutions**:
```toml
# Ensure you have at least one parameter
[[params]]
name = "n"
type = "int"
min = 1
max = 10

# For testing, set stack-size to 1 (generates all)
stack-size = 1
```

---

### Generated fewer pages than expected

**Cause**: `stack-size` limits output.

**Explanation**:
- Total documents = product of all parameter combinations
- `stack-size` controls how many are actually generated
- Set `stack-size = 1` to generate ALL documents

**Example**:
```toml
[[params]]
name = "section"
values = ["A", "B", "C"]  # 3 values

[[params]]
name = "number"
min = 1
max = 100  # 100 values

# Total combinations: 3 × 100 = 300 documents

stack-size = 1    # Generates all 300
stack-size = 50   # Generates only 50
```

---

## Examples

### Example 1: Simple Numbered Tickets

**Project structure**:
```
simple_tickets/
├── assets/
│   ├── ticket.png
│   └── Arial.ttf
└── spec.toml
```

**spec.toml**:
```toml
stack-size = 1
source-image = "assets/ticket.png"

[layout]
grid-size = [2, 4]
gap = 10
margin = 15

[[texts]]
template = "№ $number"
position = [200, 100]
size = 36
ttf = "assets/Arial.ttf"
color = "black"

[[params]]
name = "number"
type = "int"
min = 1
max = 50
leading-zeros = 3
```

**Generate**:
```bash
uv run serial-stamp generate simple_tickets -o tickets.pdf
```

**Result**: 50 tickets numbered 001-050, 8 per page.

---

### Example 2: Event Passes with Sections

**spec.toml**:
```toml
stack-size = 1
source-image = "assets/pass_background.png"

[layout]
grid-size = [3, 3]
gap = [12, 12]
margin = 20

[[texts]]
template = "PASS #$id"
position = [80, 30]
size = 28
ttf = "assets/Roboto-Bold.ttf"
color = "white"

[[texts]]
template = "Section $section"
position = [80, 80]
size = 20
ttf = "assets/Roboto-Regular.ttf"
color = [255, 215, 0]

[[params]]
name = "section"
type = "string"
values = ["VIP", "General", "Student"]

[[params]]
name = "id"
type = "int"
min = 1000
max = 1099
```

**Result**: 300 passes (3 sections × 100 IDs), 9 per page.

---

### Example 3: Vouchers with Multiple Text Fields

**spec.toml**:
```toml
stack-size = 1
source-image = "assets/voucher.png"

[layout]
grid-size = [2, 2]
gap = [20, 30]
margin = 25

[[texts]]
template = "CODE: $code"
position = [50, 100]
size = 32
ttf = "assets/Courier.ttf"
color = "black"

[[texts]]
template = "Value: $amount MGA"
position = [50, 150]
size = 24
ttf = "assets/Arial.ttf"
color = [0, 128, 0]

[[texts]]
template = "Valid until: 31/12/2024"
position = [50, 200]
size = 18
ttf = "assets/Arial.ttf"
color = [100, 100, 100]

[[params]]
name = "code"
type = "string"
values = ["SAVE10", "SAVE20", "SAVE50"]

[[params]]
name = "amount"
type = "int"
values = [10000, 20000, 50000]
```

**Result**: 9 voucher combinations (3 codes × 3 amounts).

---

## Tips & Best Practices

### 1. **Always Preview First**

Before generating large PDFs, create a preview:
```bash
uv run serial-stamp preview . -o test.png
```

### 2. **Use Leading Zeros for Professional Look**

```toml
[[params]]
name = "ticket_no"
type = "int"
min = 1
max = 1000
leading-zeros = 4  # 0001, 0002, ..., 1000
```

### 3. **Organize Fonts in Assets**

```
my_project/
├── assets/
│   ├── fonts/
│   │   ├── Roboto-Bold.ttf
│   │   ├── Roboto-Regular.ttf
│   │   └── Courier.ttf
│   └── ticket.png
└── spec.toml
```

Reference: `ttf = "assets/fonts/Roboto-Bold.ttf"`

### 4. **Test with Small Parameter Ranges**

When testing layouts, use small ranges:
```toml
# Testing
[[params]]
min = 1
max = 10  # Just 10 documents

# Production (after testing)
[[params]]
min = 1
max = 1000
```

### 5. **Use Descriptive Parameter Names**

```toml
# ✅ Good
[[params]]
name = "ticket_number"

# ❌ Avoid
[[params]]
name = "n"
```

### 6. **Archive Completed Projects**

```bash
uv run serial-stamp pack my_event -o "my_event_2024-12-15.stamp"
```

### 7. **Keep Source Images High Quality**

- Use PNG for best quality
- Ensure resolution is appropriate for printing (300 DPI recommended)
- Size documents appropriately (e.g., 800×400px for business card sized tickets)

---

## Next Steps

- 🖥️ **Desktop App** (in development): Visual editor with live preview
- 📖 **More Examples**: Check the `projects/` folder for real-world examples
- 💬 **Questions?**: Check `README.md` or ask for help

---

**Happy ticket generating! 🎫**
