# AGENT.md - SerialStamp Project Guide for AI Assistants

## Project Overview

**SerialStamp** is a tool for generating serialized documents (tickets, vouchers, invitations) by adding dynamic text and serial numbers to images, then stacking them into printable PDF pages.

The project consists of:
- **Python Backend** (`serial_stamp/`): Core image processing and PDF generation engine
- **Desktop App** (`apps/serial-stamp-desktop/`): Tauri-based desktop application with SvelteKit frontend

## Tech Stack

### Desktop Application
- **Frontend**: SvelteKit 2 with Svelte 5 (runes API)
- **Backend**: Tauri 2 (Rust)
- **Language**: TypeScript
- **Package Manager**: pnpm
- **Build Tool**: Vite

### Python Package
- **Language**: Python 3.x
- **Package Manager**: uv
- **Key Libraries**: Pillow (image processing), ReportLab (PDF generation), Pydantic (data validation)

## Project Structure

```
image_manip/
├── apps/
│   └── serial-stamp-desktop/        # Tauri desktop application
│       ├── src/
│       │   ├── lib/
│       │   │   ├── components/      # Svelte components
│       │   │   ├── icons/           # SVG icon components
│       │   │   └── state/           # Svelte state management
│       │   └── routes/              # SvelteKit routes
│       └── src-tauri/               # Rust backend (Tauri)
├── serial_stamp/                    # Python package
│   ├── gui.py                       # GUI entry point
│   ├── cli.py                       # CLI entry point
│   ├── engine.py                    # Core image/PDF generation
│   ├── models.py                    # Pydantic data models
│   └── project.py                   # Project management
├── scripts/                         # Legacy utilities
├── pyproject.toml                   # Python dependencies (uv)
└── .pre-commit-config.yaml          # Git hooks configuration
```

## Development Workflow

### Desktop App

**Location**: `apps/serial-stamp-desktop/`

**Commands**:
```bash
# Type checking
npm run check

# Development server
npm run dev

# Tauri development (with hot reload)
npm run dev:tauri

# Build
npm run build
npm run build:tauri
```

**Important Notes**:
- Uses Svelte 5 runes API (`$state`, `$derived`, `$props`, `$effect`)
- No linter configured - only type checking via `svelte-check`
- State management uses Svelte runes in `src/lib/state/*.svelte.ts` files
- Tauri commands are defined in `src-tauri/src/`

### Python Package

**Commands**:
```bash
# Install dependencies
uv sync

# Code quality
uv run ruff check .
uv run ruff format .
uv run mypy .

# Run GUI
uv run serial-stamp-gui

# Run CLI
uv run serial-stamp <command>
```

## Code Style & Conventions

### TypeScript/Svelte

1. **Component Structure**:
   - Use TypeScript interfaces for props, defined inline in component files
   - Place interfaces above the component script
   - Use Svelte 5 runes syntax (`$state`, `$props`, etc.)

2. **Type Definitions**:
   - Only extract types to separate files if reused across multiple components
   - Otherwise, define inline with `interface` declarations

3. **Naming**:
   - Components: PascalCase (e.g., `AccordionSection.svelte`)
   - State files: camelCase with `.svelte.ts` extension (e.g., `workspace.svelte.ts`)
   - Icons: PascalCase with "Icon" suffix (e.g., `ChevronIcon.svelte`)

4. **Styling**:
   - Use scoped styles within components
   - Use `:global()` selectors sparingly for cross-component styling
   - Prefer component composition over global styles

5. **Icons**:
   - Extract SVG icons into separate components in `src/lib/icons/`
   - Make icons configurable (size, class props)

### Python

1. Follow PEP 8 style guide
2. Use type hints (enforced by mypy)
3. Use Pydantic for data models and validation
4. Format with `ruff format`, lint with `ruff check`

## State Management (Desktop App)

The desktop app uses Svelte 5's runes-based reactivity:

- **`workspaceState`** (`workspace.svelte.ts`): Current project/workspace management
- **`specState`** (`spec.svelte.ts`): Document specification (layout, texts, params)
- **`resourceState`** (`resources.svelte.ts`): Images and fonts management

State is reactive and persists through Tauri commands to the Rust backend.

## Key Components

### Reusable Components

- **`AccordionGroup`**: Manages single-active accordion state with localStorage persistence
- **`AccordionSection`**: Individual accordion panel with slide transitions
- **`TextEditor`**: Form for editing text elements in the spec
- **`Sidebar`**: Left sidebar with accordion-based navigation
- **`PreviewPanel`**: Live preview of the document layout
- **`LayoutEditor`**: Canvas-based visual editor

### Icons

Located in `src/lib/icons/`, each icon is a Svelte component accepting `class` and `size` props.

## Git Workflow

### Commit Message Format

Use Conventional Commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `docs:` - Documentation changes
- `test:` - Test additions/changes

### Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:
- Trailing whitespace fix
- End of files fix
- YAML validation
- Large files check
- Python: ruff, mypy
- Desktop: pnpm check, cargo check (when applicable)

## Testing

Currently, the project has minimal automated testing. When adding tests:

### Desktop App
- Use Svelte Testing Library for component tests
- Place tests alongside components (`.test.ts` files)

### Python
- Use pytest
- Place tests in `tests/` directory
- Run with `uv run pytest`

## Common Tasks

### Adding a New Component

1. Create component file in `src/lib/components/`
2. Define TypeScript interface for props inline
3. Use Svelte 5 runes for reactivity
4. Add scoped styles
5. Export from `src/lib/index.ts` if needed

### Adding State Management

1. Create `.svelte.ts` file in `src/lib/state/`
2. Use `$state` runes for reactive values
3. Export state object with methods
4. Import and use in components

### Adding Tauri Commands

1. Define Rust function in `src-tauri/src/`
2. Use `#[tauri::command]` attribute
3. Register in `src-tauri/src/lib.rs`
4. Call from frontend using `invoke('command_name', { args })`

### Extracting SVG Icons

1. Create new `.svelte` file in `src/lib/icons/`
2. Accept `class` and `size` props
3. Use `currentColor` for `stroke`/`fill` to inherit text color
4. Make size configurable via props

## Troubleshooting

### TypeScript Errors

Run `npm run check` in the desktop app directory to see detailed errors.

### Tauri Build Issues

- Ensure Rust toolchain is up to date
- Check `src-tauri/Cargo.toml` for dependency conflicts
- Clear target directory: `rm -rf src-tauri/target`

### Python Issues

- Sync dependencies: `uv sync`
- Clear cache: `uv cache clean`
- Check Python version compatibility in `pyproject.toml`

## Architecture Decisions

### Why Svelte 5 Runes?

- Modern reactive paradigm
- Better TypeScript integration
- Cleaner state management without stores
- Fine-grained reactivity

### Why Tauri?

- Smaller bundle size than Electron
- Native performance (Rust backend)
- Better security model
- Access to system APIs

### Why uv for Python?

- Fast dependency resolution
- Lockfile support
- Modern workflow
- Compatible with pip/PyPI

## Performance Considerations

### Desktop App

- Accordion sections use virtualization for long lists
- Preview panel debounces updates
- Images are loaded asynchronously
- localStorage used for UI state persistence

### Python Backend

- PIL/Pillow for efficient image manipulation
- ReportLab for optimized PDF generation
- Batch processing for large datasets

## Future Improvements

- Add comprehensive test coverage
- Implement undo/redo functionality
- Add more export formats
- Improve preview performance with canvas rendering
- Add template library
- Implement collaborative editing features

## Resources

- [Svelte 5 Documentation](https://svelte.dev/docs/svelte/overview)
- [Tauri Documentation](https://tauri.app/v2/guides/)
- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [uv Documentation](https://docs.astral.sh/uv/)
