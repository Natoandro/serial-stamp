<script lang="ts">
    import ChevronIcon from "$lib/icons/ChevronIcon.svelte";

    interface Props {
        value: string;
        onchange?: (e: Event & { currentTarget: HTMLSelectElement }) => void;
        id?: string;
        disabled?: boolean;
        size?: "compact" | "default" | "comfortable";
        class?: string;
        ariaLabel?: string;
        children?: import("svelte").Snippet;
    }

    let {
        value = $bindable(""),
        onchange,
        id,
        disabled = false,
        size = "default",
        class: className = "",
        ariaLabel,
        children,
    }: Props = $props();
</script>

<div class="select-wrapper {size} {className}">
    <select {id} {value} {disabled} {onchange} class="select" aria-label={ariaLabel}>
        {#if children}
            {@render children()}
        {/if}
    </select>
    <ChevronIcon class="chevron" size={14} />
</div>

<style>
    .select-wrapper {
        position: relative;
        width: 100%;
    }

    .select-wrapper.compact {
        height: var(--input-height-compact);
    }

    .select-wrapper.default {
        height: var(--input-height-default);
    }

    .select-wrapper.comfortable {
        height: var(--input-height-comfortable);
    }

    .select {
        width: 100%;
        height: 100%;
        padding: 0 2rem 0 0.5rem;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        font-size: 0.9rem;
        background: var(--input-bg);
        color: var(--input-text);
        box-sizing: border-box;
        transition: border-color var(--transition-fast);
        cursor: pointer;
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
    }

    .select:hover:not(:disabled) {
        border-color: var(--input-border-hover);
    }

    .select:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .select:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    :global(.select-wrapper .chevron) {
        position: absolute;
        right: 0.5rem;
        top: 50%;
        transform: translateY(-50%);
        color: var(--text-tertiary);
        pointer-events: none;
        transition: color var(--transition-fast);
    }

    .select:hover:not(:disabled) ~ :global(.chevron) {
        color: var(--text-secondary);
    }
</style>
