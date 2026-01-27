<script lang="ts">
    interface Props {
        value: number;
        oninput?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        onchange?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        onkeydown?: (e: KeyboardEvent) => void;
        min?: number;
        max?: number;
        step?: number | string;
        placeholder?: string;
        id?: string;
        disabled?: boolean;
        readonly?: boolean;
        size?: "compact" | "default" | "comfortable";
        class?: string;
        ariaLabel?: string;
        title?: string;
    }

    let {
        value = $bindable(0),
        oninput,
        onchange,
        onkeydown,
        min,
        max,
        step = 1,
        placeholder,
        id,
        disabled = false,
        readonly = false,
        size = "default",
        class: className = "",
        ariaLabel,
        title,
    }: Props = $props();
</script>

<input
    {id}
    type="number"
    {value}
    {min}
    {max}
    {step}
    {placeholder}
    {disabled}
    {readonly}
    {title}
    {oninput}
    {onchange}
    {onkeydown}
    class="number-input {size} {className}"
    aria-label={ariaLabel}
/>

<style>
    .number-input {
        padding: 0 0.5rem;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        font-size: 0.9rem;
        background: var(--input-bg);
        color: var(--input-text);
        width: 100%;
        box-sizing: border-box;
        transition: border-color var(--transition-fast);
    }

    .number-input.compact {
        height: var(--input-height-compact);
    }

    .number-input.default {
        height: var(--input-height-default);
    }

    .number-input.comfortable {
        height: var(--input-height-comfortable);
    }

    .number-input:hover:not(:disabled) {
        border-color: var(--input-border-hover);
    }

    .number-input:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .number-input:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .number-input:read-only {
        background: var(--bg-secondary);
    }
</style>
