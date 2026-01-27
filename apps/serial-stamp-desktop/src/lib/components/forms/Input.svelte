<script lang="ts">
    interface Props {
        value: string;
        oninput?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        onchange?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        placeholder?: string;
        id?: string;
        type?: "text" | "email" | "password" | "search" | "url" | "tel";
        disabled?: boolean;
        readonly?: boolean;
        size?: "compact" | "default" | "comfortable";
        class?: string;
        ariaLabel?: string;
    }

    let {
        value = $bindable(""),
        oninput,
        onchange,
        placeholder,
        id,
        type = "text",
        disabled = false,
        readonly = false,
        size = "default",
        class: className = "",
        ariaLabel,
    }: Props = $props();
</script>

<input
    {id}
    {type}
    {value}
    {placeholder}
    {disabled}
    {readonly}
    {oninput}
    {onchange}
    class="input {size} {className}"
    aria-label={ariaLabel}
/>

<style>
    .input {
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

    .input.compact {
        height: var(--input-height-compact);
    }

    .input.default {
        height: var(--input-height-default);
    }

    .input.comfortable {
        height: var(--input-height-comfortable);
    }

    .input:hover:not(:disabled) {
        border-color: var(--input-border-hover);
    }

    .input:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .input:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .input:read-only {
        background: var(--bg-secondary);
    }
</style>
