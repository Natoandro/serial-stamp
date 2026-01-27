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
        border-bottom: 1px solid #e5e7eb;
        margin-left: -1rem;
        margin-right: -1rem;
        padding-left: 1rem;
        padding-right: 1rem;
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
        padding: 0.5rem 1rem;
        margin: 0 -1rem;
        background: none;
        border: none;
        cursor: pointer;
        width: calc(100% + 2rem);
        text-align: left;
        transition: background-color 0.15s;
        border-radius: 0;
    }

    .accordion-header:hover {
        background: rgba(0, 0, 0, 0.03);
    }

    .accordion-header:active {
        background: rgba(0, 0, 0, 0.05);
    }

    h2 {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b7280;
        font-weight: 600;
        margin: 0;
    }

    .accordion-content {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        padding-top: 0.5rem;
        flex: 1;
        min-height: 0;
        overflow-y: auto;
    }

    :global(.chevron) {
        color: #6b7280;
        transition: transform 0.2s ease;
        flex-shrink: 0;
    }

    :global(.chevron.expanded) {
        transform: rotate(180deg);
    }
</style>
