<script lang="ts">
    import GridSizeSelector from "./GridSizeSelector.svelte";
    import NumberInput from "./NumberInput.svelte";
    import Switch from "./Switch.svelte";
    import GridIcon from "$lib/icons/GridIcon.svelte";
    import ChevronIcon from "$lib/icons/ChevronIcon.svelte";

    interface Props {
        value: [number, number];
        onchange?: (size: [number, number]) => void;
        disabled?: boolean;
        class?: string;
    }

    let { value = $bindable([1, 1]), onchange, disabled = false, class: className = "" }: Props = $props();

    let popoverOpen = $state(false);
    let visualMode = $state(true);
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

    function handleManualChange(index: 0 | 1, newValue: number) {
        const newSize: [number, number] = [...value] as [number, number];
        newSize[index] = Math.max(1, Math.trunc(newValue));
        value = newSize;
        if (onchange) {
            onchange(newSize);
        }
    }

    function handleManualKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter") {
            closePopover();
        }
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
        <GridIcon class="grid-icon" size={16} />
        <span class="size-text">{value[0]} × {value[1]}</span>
        <ChevronIcon class="chevron" size={12} />
    </button>

    {#if popoverOpen}
        <div bind:this={popoverRef} class="popover">
            <div class="popover-header">
                <span class="mode-label">{visualMode ? "Visual" : "Manual"}</span>
                <Switch
                    checked={visualMode}
                    onchange={(checked) => (visualMode = checked)}
                    size="compact"
                    ariaLabel="Toggle input mode"
                />
            </div>

            {#if visualMode}
                <GridSizeSelector {value} onchange={handleSizeChange} />
            {:else}
                <div class="manual-inputs">
                    <div class="input-group">
                        <label for="manual-x">Columns</label>
                        <NumberInput
                            id="manual-x"
                            value={value[0]}
                            min={1}
                            step={1}
                            oninput={(e) => handleManualChange(0, Number(e.currentTarget.value))}
                            onkeydown={handleManualKeyDown}
                            size="compact"
                        />
                    </div>
                    <div class="input-group">
                        <label for="manual-y">Rows</label>
                        <NumberInput
                            id="manual-y"
                            value={value[1]}
                            min={1}
                            step={1}
                            oninput={(e) => handleManualChange(1, Number(e.currentTarget.value))}
                            onkeydown={handleManualKeyDown}
                            size="compact"
                        />
                    </div>
                </div>
            {/if}
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

    :global(.picker-button .grid-icon) {
        color: var(--text-secondary);
    }

    .size-text {
        flex: 1;
        text-align: left;
    }

    :global(.picker-button .chevron) {
        color: var(--text-tertiary);
        transition: color var(--transition-fast);
    }

    :global(.picker-button:hover .chevron) {
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
        min-width: 200px;
    }

    .popover-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 0.75rem;
    }

    .mode-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-secondary);
    }

    .manual-inputs {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        min-width: 150px;
    }

    .input-group {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .input-group label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-primary);
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
