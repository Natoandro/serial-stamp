/**
 * Theme System Utility
 *
 * Simple utility for switching themes via CSS classes on the root element.
 * Themes are defined in theme.css and applied by adding/removing classes.
 */

export type ThemeId = "warm-teal" | "warm-purple" | "warm-blue" | "cool-green" | "monochrome-orange" | "dark" | "auto";

export interface Theme {
  id: ThemeId;
  name: string;
  description: string;
  className: string;
}

/**
 * Available themes
 */
export const themes: Theme[] = [
  {
    id: "warm-teal",
    name: "Warm Teal",
    description: "Warm neutrals with a soft teal accent (default)",
    className: "theme-warm-teal",
  },
  {
    id: "warm-purple",
    name: "Warm Purple",
    description: "Warm neutrals with a vibrant purple accent",
    className: "theme-warm-purple",
  },
  {
    id: "warm-blue",
    name: "Warm Blue",
    description: "Warm neutrals with a vibrant blue accent",
    className: "theme-warm-blue",
  },
  {
    id: "cool-green",
    name: "Cool Green",
    description: "Cool grays with a vibrant green accent",
    className: "theme-cool-green",
  },
  {
    id: "monochrome-orange",
    name: "Monochrome Orange",
    description: "True grays with a vibrant orange accent",
    className: "theme-monochrome-orange",
  },
  {
    id: "dark",
    name: "Dark Mode",
    description: "Dark theme (experimental)",
    className: "theme-dark",
  },
  {
    id: "auto",
    name: "System Default",
    description: "Follows system dark mode preference",
    className: "theme-auto",
  },
];

/**
 * Get a theme by ID
 */
export function getTheme(id: ThemeId): Theme | undefined {
  return themes.find((theme) => theme.id === id);
}

/**
 * Apply a theme by adding its class to the root element
 */
export function applyTheme(themeId: ThemeId): void {
  const theme = getTheme(themeId);
  if (!theme) {
    console.warn(`Theme "${themeId}" not found`);
    return;
  }

  const root = document.documentElement;

  // Remove all existing theme classes
  themes.forEach((t) => {
    root.classList.remove(t.className);
  });

  // Add the new theme class (unless it's the default warm-teal)
  if (themeId !== "warm-teal") {
    root.classList.add(theme.className);
  }

  // Store theme preference
  localStorage.setItem("theme-id", themeId);
}

/**
 * Get the currently active theme ID
 */
export function getCurrentThemeId(): ThemeId {
  const root = document.documentElement;

  // Check which theme class is active
  for (const theme of themes) {
    if (root.classList.contains(theme.className)) {
      return theme.id;
    }
  }

  // Default to warm-teal if no class is found
  return "warm-teal";
}

/**
 * Load and apply the saved theme (or default)
 */
export function loadSavedTheme(): void {
  const savedThemeId = localStorage.getItem("theme-id") as ThemeId | null;
  const themeId = savedThemeId && getTheme(savedThemeId) ? savedThemeId : "warm-teal";

  applyTheme(themeId);
}
