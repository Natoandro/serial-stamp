# Theme System

A modern, customizable theming system using **pure CSS** with class-based switching and the OKLCh color space for perceptually uniform colors.

## Features

- **Pure CSS**: All themes defined in CSS, no runtime JS color manipulation
- **Class-Based Switching**: Simple theme switching via CSS classes on root element
- **Modern CSS**: Uses OKLCh color space for better color perception
- **Type-Safe**: TypeScript utilities for theme management
- **Persistent**: Theme preferences saved to localStorage
- **Future-Ready**: Built with theme switcher UI in mind

## Usage

### Applying a Theme

Themes are automatically loaded on app mount. To change themes programmatically:

```typescript
import { applyTheme } from '$lib/themes/themes';

// Apply a theme by ID
applyTheme('warm-purple');
```

The `applyTheme()` function simply adds/removes CSS classes on `document.documentElement`:

```typescript
// Behind the scenes:
document.documentElement.classList.add('theme-warm-purple');
```

### Available Themes

1. **Warm Teal** (default) - Warm neutrals with soft teal accent
2. **Warm Purple** - Warm neutrals with vibrant purple accent
3. **Warm Blue** - Warm neutrals with vibrant blue accent
4. **Cool Green** - Cool grays with vibrant green accent
5. **Monochrome Orange** - True grays with vibrant orange accent

### Using Theme Variables in Components

All components should use CSS custom properties instead of hardcoded colors:

```svelte
<style>
  .my-component {
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-normal);
  }

  .my-component:hover {
    background: var(--bg-hover);
  }
</style>
```

## CSS Custom Properties

### Colors

#### Backgrounds
- `--bg-primary` - Main background
- `--bg-secondary` - Secondary background
- `--bg-tertiary` - Tertiary background
- `--bg-elevated` - Elevated surfaces
- `--bg-accent-subtle` - Subtle accent background
- `--bg-accent-muted` - Muted accent background
- `--bg-hover` - Hover state background
- `--bg-active` - Active state background

#### Text
- `--text-primary` - Primary text
- `--text-secondary` - Secondary text
- `--text-tertiary` - Tertiary/muted text
- `--text-accent` - Accent color text
- `--text-on-accent` - Text on accent backgrounds

#### Borders
- `--border-subtle` - Subtle border
- `--border-normal` - Normal border
- `--border-strong` - Strong border
- `--border-accent` - Accent border
- `--border-focus` - Focus ring border

#### Interactive
- `--interactive-normal` - Normal interactive elements
- `--interactive-hover` - Hover state
- `--interactive-active` - Active/pressed state
- `--interactive-disabled` - Disabled state

#### States
- `--state-success` - Success state (green)
- `--state-warning` - Warning state (amber)
- `--state-error` - Error state (red)
- `--state-info` - Info state (teal/accent)

### Component-Specific

#### Sidebar
- `--sidebar-bg`
- `--sidebar-border`
- `--sidebar-header-text`
- `--sidebar-text`

#### Accordion
- `--accordion-border`
- `--accordion-header-bg`
- `--accordion-header-bg-hover`
- `--accordion-header-bg-active`
- `--accordion-header-text`
- `--accordion-content-bg`
- `--accordion-chevron`
- `--accordion-chevron-active`

#### Inputs
- `--input-bg`
- `--input-border`
- `--input-border-hover`
- `--input-border-focus`
- `--input-text`
- `--input-placeholder`

#### Buttons
- `--button-primary-bg`
- `--button-primary-bg-hover`
- `--button-primary-text`
- `--button-secondary-bg`
- `--button-secondary-bg-hover`
- `--button-secondary-border`
- `--button-secondary-text`

#### Icons
- `--icon-primary`
- `--icon-secondary`
- `--icon-accent`
- `--icon-hover`

### Spacing
- `--space-1` to `--space-8` - Consistent spacing scale

### Border Radius
- `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`, `--radius-full`

### Shadows
- `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`

### Transitions
- `--transition-fast` (150ms)
- `--transition-base` (200ms)
- `--transition-slow` (300ms)

### Easing Functions
- `--ease-in-out`
- `--ease-out`
- `--ease-in`

## Creating a Custom Theme

1. Define your theme colors in `theme.css`:

```css
:root.theme-my-custom {
  /* Neutral colors */
  --color-neutral-0: oklch(99% 0.005 85);
  --color-neutral-50: oklch(98% 0.008 85);
  /* ... define all neutral colors */

  /* Accent colors */
  --color-accent-50: oklch(96% 0.03 200);
  --color-accent-100: oklch(92% 0.05 200);
  /* ... define all accent colors */

  /* State colors */
  --state-success: oklch(70% 0.15 145);
  --state-warning: oklch(75% 0.15 80);
  --state-error: oklch(60% 0.18 25);
  --state-info: oklch(55% 0.14 200);
}
```

2. Register the theme in `themes.ts`:

```typescript
export const themes: Theme[] = [
  // ... existing themes
  {
    id: "my-custom",
    name: "My Custom Theme",
    description: "A custom theme description",
    className: "theme-my-custom",
  },
];
```

3. Apply it:

```typescript
import { applyTheme } from '$lib/themes/themes';
applyTheme('my-custom');
```

## OKLCh Color Space

OKLCh provides perceptually uniform colors:
- **L** (Lightness): 0-100%
- **C** (Chroma): 0-0.4 (saturation)
- **H** (Hue): 0-360 degrees

Example: `oklch(65% 0.12 200)` = 65% lightness, 0.12 chroma, 200° hue (teal)

### Hue Reference
- 0° = Red
- 50° = Orange
- 80° = Yellow
- 145° = Green
- 200° = Cyan/Teal
- 240° = Blue
- 300° = Purple/Magenta

## Dark Mode Support

Dark mode is built into the theme system. To enable:

```typescript
// Apply dark mode
applyTheme('dark');

// Or use system preference (follows OS dark mode)
applyTheme('auto');
```

The `theme-auto` class uses `@media (prefers-color-scheme: dark)` to automatically switch based on system preferences.

## How It Works

### Class-Based Theming

All themes are defined as CSS rulesets targeting `:root.theme-{name}`:

```css
/* Default theme (no class needed) */
:root {
  --color-accent-500: oklch(55% 0.14 200); /* Teal */
}

/* Purple theme (activated via .theme-warm-purple class) */
:root.theme-warm-purple {
  --color-accent-500: oklch(55% 0.2 300); /* Purple */
}
```

When you call `applyTheme('warm-purple')`, it:
1. Removes all existing theme classes
2. Adds `theme-warm-purple` class to `<html>`
3. CSS cascade applies the new colors instantly

### Benefits

✅ **No JavaScript color manipulation** - Pure CSS, instant switching
✅ **No inline styles** - Clean, maintainable code
✅ **Better performance** - Browser handles all color changes
✅ **SSR-friendly** - Works with server-side rendering
✅ **Easy debugging** - Just inspect CSS classes

## Future Enhancements

- Theme switcher UI component
- More preset themes
- Theme import/export (JSON → CSS)
- Per-component theme overrides
- Color contrast validation
- Theme preview generator
