# Theme Switcher Component Example

This file shows how to create a theme switcher UI component using the theme system.

## Simple Theme Switcher Component

```svelte
<!-- ThemeSwitcher.svelte -->
<script lang="ts">
  import { applyTheme, themes, getCurrentThemeId, type ThemeId } from '$lib/themes/themes';

  let currentTheme = $state<ThemeId>('warm-teal');

  // Update current theme on mount
  $effect(() => {
    if (typeof window !== 'undefined') {
      currentTheme = getCurrentThemeId();
    }
  });

  function handleThemeChange(themeId: ThemeId) {
    applyTheme(themeId);
    currentTheme = themeId;
  }
</script>

<div class="theme-switcher">
  <label for="theme-select">Theme:</label>
  <select
    id="theme-select"
    value={currentTheme}
    onchange={(e) => handleThemeChange(e.currentTarget.value as ThemeId)}
  >
    {#each themes as theme}
      <option value={theme.id}>{theme.name}</option>
    {/each}
  </select>
</div>

<style>
  .theme-switcher {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2);
  }

  label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
  }

  select {
    padding: var(--space-2);
    border: 1px solid var(--input-border);
    border-radius: var(--radius-md);
    background: var(--input-bg);
    color: var(--input-text);
    font-size: 0.875rem;
    cursor: pointer;
    transition: border-color var(--transition-fast);
  }

  select:hover {
    border-color: var(--input-border-hover);
  }

  select:focus {
    outline: none;
    border-color: var(--input-border-focus);
    box-shadow: 0 0 0 3px var(--bg-accent-subtle);
  }
</style>
```

## Dropdown Theme Switcher

```svelte
<!-- ThemeSwitcherDropdown.svelte -->
<script lang="ts">
  import { applyTheme, themes, getCurrentThemeId, type ThemeId } from '$lib/themes/themes';

  let currentTheme = $state<ThemeId>('warm-teal');
  let isOpen = $state(false);

  $effect(() => {
    if (typeof window !== 'undefined') {
      currentTheme = getCurrentThemeId();
    }
  });

  function handleThemeSelect(themeId: ThemeId) {
    applyTheme(themeId);
    currentTheme = themeId;
    isOpen = false;
  }

  function toggleDropdown() {
    isOpen = !isOpen;
  }

  const currentThemeObj = $derived(themes.find(t => t.id === currentTheme));
</script>

<div class="theme-dropdown">
  <button
    class="theme-button"
    onclick={toggleDropdown}
    aria-expanded={isOpen}
    aria-haspopup="true"
  >
    <span class="theme-icon">🎨</span>
    <span>{currentThemeObj?.name ?? 'Theme'}</span>
    <span class="chevron" class:open={isOpen}>▼</span>
  </button>

  {#if isOpen}
    <div class="dropdown-menu">
      {#each themes as theme}
        <button
          class="theme-option"
          class:active={theme.id === currentTheme}
          onclick={() => handleThemeSelect(theme.id)}
        >
          <div class="theme-info">
            <span class="theme-name">{theme.name}</span>
            <span class="theme-desc">{theme.description}</span>
          </div>
          {#if theme.id === currentTheme}
            <span class="check">✓</span>
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .theme-dropdown {
    position: relative;
  }

  .theme-button {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    background: var(--bg-primary);
    border: 1px solid var(--border-normal);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .theme-button:hover {
    background: var(--bg-hover);
    border-color: var(--border-strong);
  }

  .theme-icon {
    font-size: 1.125rem;
  }

  .chevron {
    margin-left: auto;
    font-size: 0.625rem;
    transition: transform var(--transition-fast);
  }

  .chevron.open {
    transform: rotate(180deg);
  }

  .dropdown-menu {
    position: absolute;
    top: calc(100% + var(--space-1));
    right: 0;
    min-width: 280px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-normal);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-lg);
    padding: var(--space-1);
    z-index: 100;
  }

  .theme-option {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3);
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background-color var(--transition-fast);
    text-align: left;
  }

  .theme-option:hover {
    background: var(--bg-hover);
  }

  .theme-option.active {
    background: var(--bg-accent-subtle);
  }

  .theme-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .theme-name {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
  }

  .theme-desc {
    font-size: 0.75rem;
    color: var(--text-tertiary);
  }

  .check {
    color: var(--text-accent);
    font-weight: bold;
  }
</style>
```

## Radio Button Theme Switcher

```svelte
<!-- ThemeSwitcherRadio.svelte -->
<script lang="ts">
  import { applyTheme, themes, getCurrentThemeId, type ThemeId } from '$lib/themes/themes';

  let currentTheme = $state<ThemeId>('warm-teal');

  $effect(() => {
    if (typeof window !== 'undefined') {
      currentTheme = getCurrentThemeId();
    }
  });

  function handleChange(themeId: ThemeId) {
    applyTheme(themeId);
    currentTheme = themeId;
  }
</script>

<div class="theme-radio-group">
  <h3>Choose Theme</h3>

  <div class="radio-list">
    {#each themes as theme}
      <label class="radio-option">
        <input
          type="radio"
          name="theme"
          value={theme.id}
          checked={currentTheme === theme.id}
          onchange={() => handleChange(theme.id)}
        />
        <div class="radio-label">
          <span class="radio-name">{theme.name}</span>
          <span class="radio-desc">{theme.description}</span>
        </div>
      </label>
    {/each}
  </div>
</div>

<style>
  .theme-radio-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  h3 {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .radio-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .radio-option {
    display: flex;
    align-items: flex-start;
    gap: var(--space-2);
    padding: var(--space-3);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .radio-option:hover {
    background: var(--bg-hover);
    border-color: var(--border-normal);
  }

  .radio-option:has(input:checked) {
    background: var(--bg-accent-subtle);
    border-color: var(--border-accent);
  }

  input[type="radio"] {
    margin-top: 2px;
    cursor: pointer;
    accent-color: var(--interactive-normal);
  }

  .radio-label {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .radio-name {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary);
  }

  .radio-desc {
    font-size: 0.75rem;
    color: var(--text-tertiary);
  }
</style>
```

## Inline Theme Switcher (Icon Grid)

```svelte
<!-- ThemeSwitcherGrid.svelte -->
<script lang="ts">
  import { applyTheme, getCurrentThemeId, type ThemeId } from '$lib/themes/themes';

  let currentTheme = $state<ThemeId>('warm-teal');

  $effect(() => {
    if (typeof window !== 'undefined') {
      currentTheme = getCurrentThemeId();
    }
  });

  // Theme color previews (accent color for each theme)
  const themeColors: Record<ThemeId, string> = {
    'warm-teal': 'oklch(55% 0.14 200)',
    'warm-purple': 'oklch(55% 0.2 300)',
    'warm-blue': 'oklch(55% 0.19 240)',
    'cool-green': 'oklch(55% 0.2 145)',
    'monochrome-orange': 'oklch(55% 0.22 50)',
    'dark': 'oklch(20% 0.008 75)',
    'auto': 'oklch(60% 0.025 75)',
  };

  function handleThemeClick(themeId: ThemeId) {
    applyTheme(themeId);
    currentTheme = themeId;
  }
</script>

<div class="theme-grid">
  {#each Object.entries(themeColors) as [themeId, color]}
    <button
      class="theme-swatch"
      class:active={currentTheme === themeId}
      style:--theme-color={color}
      onclick={() => handleThemeClick(themeId as ThemeId)}
      title={themeId.replace(/-/g, ' ')}
      aria-label="Switch to {themeId} theme"
    >
      {#if currentTheme === themeId}
        <span class="check">✓</span>
      {/if}
    </button>
  {/each}
</div>

<style>
  .theme-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(40px, 1fr));
    gap: var(--space-2);
    max-width: 320px;
  }

  .theme-swatch {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    background: var(--theme-color);
    border: 2px solid transparent;
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  .theme-swatch:hover {
    border-color: var(--border-accent);
    transform: scale(1.1);
  }

  .theme-swatch.active {
    border-color: var(--text-accent);
    box-shadow: var(--shadow-md);
  }

  .check {
    color: white;
    font-weight: bold;
    font-size: 1.125rem;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  }
</style>
```

## Usage in App

Add the theme switcher to your app layout or settings panel:

```svelte
<!-- +layout.svelte or SettingsPanel.svelte -->
<script lang="ts">
  import ThemeSwitcher from '$lib/components/ThemeSwitcher.svelte';
  // Or any of the other variants
</script>

<div class="app-header">
  <h1>My App</h1>
  <ThemeSwitcher />
</div>
```

## Programmatic Theme Switching

You can also switch themes programmatically:

```typescript
import { applyTheme } from '$lib/themes/themes';

// Switch on user action
function onDarkModeToggle(isDark: boolean) {
  applyTheme(isDark ? 'dark' : 'warm-teal');
}

// Switch based on time of day
function applyTimeBasedTheme() {
  const hour = new Date().getHours();
  const isDaytime = hour >= 6 && hour < 18;
  applyTheme(isDaytime ? 'warm-teal' : 'dark');
}

// Switch based on route
function applyRouteTheme(route: string) {
  if (route.startsWith('/admin')) {
    applyTheme('monochrome-orange');
  } else {
    applyTheme('warm-teal');
  }
}
```
