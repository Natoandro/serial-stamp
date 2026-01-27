<script lang="ts">
    import GridSizeSelector from "./GridSizeSelector.svelte";

    interface Props {
        value: [number, number];
        onchange?: (size: [number, number]) => void;
        disabled?: boolean;
        class?: string;
    }

    let {
        value = $bindable([1, 1]),
        onchange,
        disabled = false,
        class: className = "",
    }: Props = $props();

    let popoverOpen = $state(false);
    let buttonRef: HTMLButtonElement | undefined = $state();
    let popoverRef: HTMLDivElement | undefined = $state();

    function openPopover() {
        if (disabled) return;
        popoverOpen = true;
    }

    function closePopover() {
        popoverOpen = false;
    }

    function handleSizeChange(size: [number, number]) {
        if (onchange) {
            onchange(size);
        }
        closePopover();
    }

    // Close popover when clicking outside
    function handleClickOutside(event: MouseEvent) {
        if (
            popoverOpen &&
            popoverRef &&
            buttonRef &&
            !popoverRef.contains(event.target as Node) &&
            !buttonRef.contains(event.target as Node)
        ) {
            closePopover();
        }
    }

    $effect(() => {
        if (popoverOpen) {
            document.addEventListener("mousedown", handleClickOutside);
            return () => {
                document.removeEventListener("mousedown", handleClickOutside);
            };
        }
    });
</script>

<div class="grid-size-picker {className}">
    <button
        bind:this={buttonRef}
        type="button"
        class="picker-button"
        onclick={openPopover}
        {disabled}
        aria-label="Select grid size"
    >
        <span class="grid-icon">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
            >
                <rect x="2" y="2" width="5" height="5" />
                <rect x="9" y="2" width="5" height="5" />
                <rect x="2" y="9" width="5" height="5" />
                <rect x="9" y="9" width="5" height="5" />
            </svg>
        </span>
        <span class="size-text">{value[0]} × {value[1]}</span>
        <span class="chevron">▾</span>
    </button>

    {#if popoverOpen}
        <div bind:this={popoverRef} class="popover">
            <GridSizeSelector value={value} onchange={handleSizeChange} />
        </div>
    {/if}
</div>

<style>
    .grid-size-picker {
        position: relative;
        width: 100%;
    }

    .picker-button {
        width: 100%;
        height: var(--input-height-default);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0 0.5rem;
        background: var(--input-bg);
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        color: var(--text-primary);
        font-size: 0.9rem;
        cursor: pointer;
        transition: all var(--transition-fast);
    }

    .picker-button:hover:not(:disabled) {
        border-color: var(--input-border-hover);
    }

    .picker-button:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .picker-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .grid-icon {
        display: flex;
        align-items: center;
        color: var(--text-secondary);
    }

    .size-text {
        flex: 1;
        text-align: left;
    }

    .chevron {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        transition: transform var(--transition-fast);
    }

    .picker-button:hover .chevron {
        color: var(--text-secondary);
    }

    .popover {
        position: absolute;
        top: calc(100% + 0.5rem);
        left: 0;
        z-index: 1000;
        background: var(--bg-primary);
        border: 1px solid var(--border-normal);
        border-radius: var(--radius-md);
        padding: 0.75rem;
        box-shadow: var(--shadow-lg);
        animation: popover-appear 0.15s ease-out;
    }

    @keyframes popover-appear {
        from {
            opacity: 0;
            transform: translateY(-0.5rem);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
