<script lang="ts">
    interface Props {
        value: string;
        oninput?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        onchange?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        id?: string;
        disabled?: boolean;
        size?: "compact" | "default" | "comfortable";
        class?: string;
        ariaLabel?: string;
    }

    let {
        value = $bindable(""),
        oninput,
        onchange,
        id,
        disabled = false,
        size = "default",
        class: className = "",
        ariaLabel,
    }: Props = $props();

    // Compute color picker value from text input
    let colorPickerValue = $derived(typeof value === "string" && value.startsWith("#") ? value : "#000000");
</script>

<div class="color-input-wrapper {size} {className}">
    <input
        {id}
        type="color"
        value={colorPickerValue}
        {disabled}
        {oninput}
        {onchange}
        class="color-box"
        aria-label={ariaLabel ?? "Color picker"}
    />
</div>

<style>
    .color-input-wrapper {
        display: flex;
        width: 100%;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        padding: 4px;
        box-sizing: border-box;
        transition: border-color var(--transition-fast);
        background: var(--input-bg);
    }

    .color-input-wrapper:hover:not(:has(input:disabled)) {
        border-color: var(--input-border-hover);
    }

    .color-input-wrapper:has(input:focus) {
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .color-input-wrapper.compact {
        height: var(--input-height-compact);
    }

    .color-input-wrapper.default {
        height: var(--input-height-default);
    }

    .color-input-wrapper.comfortable {
        height: var(--input-height-comfortable);
    }

    .color-box {
        width: 100%;
        height: 100%;
        border: 1px solid var(--border-subtle);
        border-radius: calc(var(--radius-md) - 2px);
        padding: 0;
        margin: 0;
        cursor: pointer;
        background: none;
    }

    .color-box:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .color-box:focus {
        outline: none;
    }

    /* Remove default color input styling in WebKit browsers */
    .color-box::-webkit-color-swatch-wrapper {
        padding: 0;
    }

    .color-box::-webkit-color-swatch {
        border: none;
        border-radius: 0;
    }

    /* Remove default color input styling in Firefox */
    .color-box::-moz-color-swatch {
        border: none;
    }
</style>
