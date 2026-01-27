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

<div class="color-input-wrapper {className}">
    <input
        {id}
        type="text"
        {value}
        {disabled}
        {oninput}
        {onchange}
        class="color-text-input {size}"
        aria-label={ariaLabel ?? "Color text input"}
    />
    <input
        type="color"
        value={colorPickerValue}
        {disabled}
        {oninput}
        {onchange}
        class="color-picker {size}"
        aria-label={ariaLabel ? `${ariaLabel} picker` : "Color picker"}
    />
</div>

<style>
    .color-input-wrapper {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        width: 100%;
    }

    .color-text-input {
        flex: 1;
        min-width: 0;
        padding: 0 0.5rem;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        font-size: 0.9rem;
        background: var(--input-bg);
        color: var(--input-text);
        box-sizing: border-box;
        transition: border-color var(--transition-fast);
    }

    .color-text-input.compact {
        height: var(--input-height-compact);
    }

    .color-text-input.default {
        height: var(--input-height-default);
    }

    .color-text-input.comfortable {
        height: var(--input-height-comfortable);
    }

    .color-text-input:hover:not(:disabled) {
        border-color: var(--input-border-hover);
    }

    .color-text-input:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .color-text-input:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .color-picker {
        padding: 2px;
        cursor: pointer;
        flex-shrink: 0;
        border: none;
        background: none;
        border-radius: var(--radius-sm);
    }

    .color-picker.compact {
        width: var(--input-height-compact);
        height: var(--input-height-compact);
    }

    .color-picker.default {
        width: var(--input-height-default);
        height: var(--input-height-default);
    }

    .color-picker.comfortable {
        width: var(--input-height-comfortable);
        height: var(--input-height-comfortable);
    }

    .color-picker:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .color-picker:focus {
        outline: 2px solid var(--input-border-focus);
        outline-offset: 2px;
    }
</style>
