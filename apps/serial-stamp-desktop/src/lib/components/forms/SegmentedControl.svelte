<script lang="ts">
    interface Option {
        value: string;
        label: string;
    }

    interface Props {
        options: Option[];
        value: string;
        onchange?: (value: string) => void;
        id?: string;
        size?: "compact" | "default" | "comfortable";
        class?: string;
    }

    let { options, value = $bindable(""), onchange, id, size = "default", class: className = "" }: Props = $props();

    function handleClick(optionValue: string) {
        if (value !== optionValue) {
            value = optionValue;
            onchange?.(optionValue);
        }
    }

    function handleKeydown(e: KeyboardEvent, optionValue: string) {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleClick(optionValue);
        }
    }
</script>

<div
    class="segmented-control {className}"
    class:compact={size === "compact"}
    class:comfortable={size === "comfortable"}
    role="radiogroup"
    {id}
>
    {#each options as option}
        <button
            type="button"
            class="segment"
            class:active={value === option.value}
            onclick={() => handleClick(option.value)}
            onkeydown={(e) => handleKeydown(e, option.value)}
            role="radio"
            aria-checked={value === option.value}
            tabindex={value === option.value ? 0 : -1}
        >
            {option.label}
        </button>
    {/each}
</div>

<style>
    .segmented-control {
        display: inline-flex;
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        padding: 2px;
        gap: 2px;
        margin-left: auto;
    }

    .segment {
        flex: 0 0 auto;
        padding: 0.375rem 0.75rem;
        border: none;
        background: transparent;
        color: var(--text-secondary);
        font-size: 0.75rem;
        font-weight: 500;
        border-radius: calc(var(--radius-sm) - 2px);
        cursor: pointer;
        transition: all 0.15s ease;
        white-space: nowrap;
        user-select: none;
    }

    .segment:hover:not(.active) {
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .segment.active {
        background: var(--bg-primary);
        color: var(--text-primary);
        font-weight: 600;
        box-shadow:
            0 1px 3px rgba(0, 0, 0, 0.1),
            0 0 0 1px var(--border-subtle);
    }

    .segment:focus-visible {
        outline: 2px solid var(--focus-ring);
        outline-offset: -2px;
        z-index: 1;
    }

    /* Size variants */
    .segmented-control.compact .segment {
        padding: 0.25rem 0.625rem;
        font-size: 0.7rem;
    }

    .segmented-control.comfortable .segment {
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
    }
</style>
