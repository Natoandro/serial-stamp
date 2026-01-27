<script lang="ts">
    import { onMount } from "svelte";

    interface AccordionGroupProps {
        storageKey: string;
        defaultExpanded?: string;
        children: any;
    }

    let { storageKey, defaultExpanded = "", children }: AccordionGroupProps = $props();

    let expandedSection = $state<string | null>(null);

    onMount(() => {
        // Load from localStorage
        const stored = localStorage.getItem(storageKey);
        if (stored) {
            try {
                expandedSection = stored;
            } catch {
                expandedSection = defaultExpanded || null;
            }
        } else {
            // Initialize with default if no stored value
            expandedSection = defaultExpanded || null;
        }
    });

    export function isExpanded(sectionId: string): boolean {
        return expandedSection === sectionId;
    }

    export function toggle(sectionId: string): void {
        // Single-active: clicking the same section collapses it, otherwise switch to new section
        if (expandedSection === sectionId) {
            expandedSection = null;
        } else {
            expandedSection = sectionId;
        }

        // Persist to localStorage
        localStorage.setItem(storageKey, expandedSection || "");
    }
</script>

{@render children({ isExpanded, toggle })}

<style>
    /* No styles needed - this is a logical component */
</style>
