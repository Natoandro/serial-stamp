<script lang="ts">
    import { slide } from "svelte/transition";
    import ChevronIcon from "$lib/icons/ChevronIcon.svelte";

    interface AccordionSectionProps {
        title: string;
        expanded?: boolean;
        onclick?: () => void;
        children: any;
    }

    let { title, expanded = false, onclick, children }: AccordionSectionProps = $props();

    function handleClick() {
        if (onclick) {
            onclick();
        }
    }
</script>

<div class="accordion-section" class:expanded>
    <button class="accordion-header" onclick={handleClick} type="button">
        <h2>{title}</h2>
        <ChevronIcon class={expanded ? "chevron expanded" : "chevron"} size={16} />
    </button>
    {#if expanded}
        <div class="accordion-content" transition:slide={{ duration: 200 }}>
            {@render children()}
        </div>
    {/if}
</div>

<style>
    .accordion-section {
        display: flex;
        flex-direction: column;
        border-bottom: 1px solid var(--accordion-border);
        margin-left: calc(var(--space-4) * -1);
        margin-right: calc(var(--space-4) * -1);
        padding-left: var(--space-4);
        padding-right: var(--space-4);
    }

    .accordion-section.expanded {
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;
    }

    .accordion-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--space-2) var(--space-4);
        margin: 0 calc(var(--space-4) * -1);
        background: var(--accordion-header-bg);
        border: none;
        cursor: pointer;
        width: calc(100% + var(--space-4) * 2);
        text-align: left;
        transition: background-color var(--transition-fast);
        border-radius: 0;
    }

    .accordion-header:hover {
        background: var(--accordion-header-bg-hover);
    }

    .accordion-header:active {
        background: var(--accordion-header-bg-active);
    }

    h2 {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--accordion-header-text);
        font-weight: 600;
        margin: 0;
        transition: color var(--transition-fast);
    }

    .accordion-content {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
        padding-top: var(--space-2);
        flex: 1;
        min-height: 0;
        overflow-y: auto;
        background: var(--accordion-content-bg);
    }

    :global(.chevron) {
        color: var(--accordion-chevron);
        transition:
            transform var(--transition-base),
            color var(--transition-fast);
        flex-shrink: 0;
    }

    :global(.chevron.expanded) {
        transform: rotate(180deg);
        color: var(--accordion-chevron-active);
    }
</style>
