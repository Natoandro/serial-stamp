<script lang="ts">
    import ChevronIcon from "$lib/icons/ChevronIcon.svelte";
    import { onMount } from "svelte";

    interface Option {
        value: string;
        label: string;
        disabled?: boolean;
    }

    interface ActionOption {
        label: string;
        action: () => void | Promise<void>;
        disabled?: boolean;
    }

    interface Props {
        value: string;
        options?: Option[];
        actionOptions?: ActionOption[];
        onchange?: (value: string) => void;
        id?: string;
        disabled?: boolean;
        size?: "compact" | "default" | "comfortable";
        class?: string;
        ariaLabel?: string;
        placeholder?: string;
        children?: import("svelte").Snippet;
        optionContent?: import("svelte").Snippet<[Option]>;
    }

    let {
        value = $bindable(""),
        options = [],
        actionOptions = [],
        onchange,
        id,
        disabled = false,
        size = "default",
        class: className = "",
        ariaLabel,
        placeholder = "Select an option",
        children,
        optionContent,
    }: Props = $props();

    let isOpen = $state(false);
    let buttonRef: HTMLButtonElement | undefined = $state();
    let popoverRef: HTMLDivElement | undefined = $state();
    let selectRef: HTMLSelectElement | undefined = $state();
    let focusedIndex = $state(-1);

    // Determine if using legacy mode (children snippet with native options)
    const useLegacyMode = $derived(!!children && options.length === 0);

    // Extract options from select element when in legacy mode
    let legacyOptions = $state<Option[]>([]);

    $effect(() => {
        if (useLegacyMode && selectRef) {
            const opts: Option[] = [];
            const optionElements = selectRef.querySelectorAll("option");
            optionElements.forEach((el) => {
                opts.push({
                    value: el.value,
                    label: el.textContent || el.value,
                    disabled: el.disabled,
                });
            });
            legacyOptions = opts;
        }
    });

    const effectiveOptions = $derived(useLegacyMode ? legacyOptions : options);
    const selectedOption = $derived(effectiveOptions.find((opt) => opt.value === value));
    const selectedLabel = $derived(selectedOption?.label || placeholder);
    const availableOptions = $derived(effectiveOptions.filter((opt) => !opt.disabled));

    function togglePopover() {
        if (disabled) return;
        isOpen = !isOpen;
        if (isOpen) {
            focusedIndex = availableOptions.findIndex((opt) => opt.value === value);
            if (focusedIndex === -1) focusedIndex = 0;
        }
    }

    function closePopover() {
        isOpen = false;
        focusedIndex = -1;
        buttonRef?.focus();
    }

    function selectOption(option: Option) {
        if (option.disabled) return;
        value = option.value;
        onchange?.(option.value);
        closePopover();
    }

    async function executeAction(actionOption: ActionOption) {
        if (actionOption.disabled) return;
        closePopover();
        await actionOption.action();
    }

    function handleKeydown(e: KeyboardEvent) {
        if (disabled) return;

        switch (e.key) {
            case "Enter":
            case " ":
                if (!isOpen) {
                    e.preventDefault();
                    togglePopover();
                } else if (focusedIndex >= 0 && focusedIndex < availableOptions.length) {
                    e.preventDefault();
                    selectOption(availableOptions[focusedIndex]);
                }
                break;
            case "Escape":
                if (isOpen) {
                    e.preventDefault();
                    closePopover();
                }
                break;
            case "ArrowDown":
                e.preventDefault();
                if (!isOpen) {
                    togglePopover();
                } else {
                    focusedIndex = Math.min(focusedIndex + 1, availableOptions.length - 1);
                }
                break;
            case "ArrowUp":
                e.preventDefault();
                if (isOpen) {
                    focusedIndex = Math.max(focusedIndex - 1, 0);
                }
                break;
            case "Tab":
                if (isOpen) {
                    closePopover();
                }
                break;
        }
    }

    function handleClickOutside(e: MouseEvent) {
        if (
            isOpen &&
            buttonRef &&
            popoverRef &&
            !buttonRef.contains(e.target as Node) &&
            !popoverRef.contains(e.target as Node)
        ) {
            closePopover();
        }
    }

    onMount(() => {
        document.addEventListener("click", handleClickOutside);
        return () => {
            document.removeEventListener("click", handleClickOutside);
        };
    });

    $effect(() => {
        if (isOpen && popoverRef && focusedIndex >= 0) {
            const focusedElement = popoverRef.querySelector(`[data-option-index="${focusedIndex}"]`) as HTMLElement;
            focusedElement?.scrollIntoView({ block: "nearest" });
        }
    });
</script>

<!-- Hidden select for legacy mode (extracts options from children) -->
{#if useLegacyMode}
    <select bind:this={selectRef} style="display: none;" aria-hidden="true">
        {#if children}
            {@render children()}
        {/if}
    </select>
{/if}

<div class="select-wrapper {size} {className}">
    <button
        bind:this={buttonRef}
        {id}
        type="button"
        class="select-button"
        class:open={isOpen}
        class:has-value={!!selectedOption}
        {disabled}
        onkeydown={handleKeydown}
        onclick={togglePopover}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={ariaLabel}
    >
        <span class="selected-text">
            {selectedLabel}
        </span>
        <ChevronIcon class="chevron {isOpen ? 'rotate' : ''}" size={14} />
    </button>

    {#if isOpen}
        <div bind:this={popoverRef} class="popover" role="listbox">
            {#each actionOptions as actionOption}
                <button
                    type="button"
                    class="option action-option"
                    disabled={actionOption.disabled}
                    onclick={() => executeAction(actionOption)}
                >
                    {actionOption.label}
                </button>
            {/each}
            {#each availableOptions as option, index (option.value)}
                <button
                    type="button"
                    class="option"
                    class:selected={option.value === value}
                    class:focused={index === focusedIndex}
                    disabled={option.disabled}
                    onclick={() => selectOption(option)}
                    role="option"
                    aria-selected={option.value === value}
                    data-option-index={index}
                >
                    {#if optionContent}
                        {@render optionContent(option)}
                    {:else}
                        {option.label}
                    {/if}
                </button>
            {/each}
        </div>
    {/if}
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

    .select-button {
        width: 100%;
        height: 100%;
        padding: 0 2rem 0 0.75rem;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        font-size: 0.9rem;
        background: var(--input-bg);
        color: var(--input-text);
        box-sizing: border-box;
        transition: all var(--transition-fast);
        cursor: pointer;
        display: flex;
        align-items: center;
        text-align: left;
    }

    .select-button:not(.has-value) .selected-text {
        color: var(--text-tertiary);
    }

    .select-button:hover:not(:disabled) {
        border-color: var(--input-border-hover);
    }

    .select-button:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .select-button.open {
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .select-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .selected-text {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    :global(.select-wrapper .chevron) {
        position: absolute;
        right: 0.5rem;
        top: 50%;
        transform: translateY(-50%);
        color: var(--text-tertiary);
        pointer-events: none;
        transition: all var(--transition-fast);
    }

    :global(.select-wrapper .chevron.rotate) {
        transform: translateY(-50%) rotate(180deg);
    }

    .select-button:hover:not(:disabled) :global(.chevron) {
        color: var(--text-secondary);
    }

    .popover {
        position: absolute;
        top: calc(100% + 4px);
        left: 0;
        right: 0;
        max-height: 16rem;
        overflow-y: auto;
        background: var(--bg-primary);
        border: 1px solid var(--border-normal);
        border-radius: var(--radius-md);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        padding: 0.25rem;
    }

    .option {
        width: 100%;
        padding: 0.5rem 0.75rem;
        border: none;
        background: transparent;
        color: var(--text-primary);
        font-size: 0.9rem;
        text-align: left;
        cursor: pointer;
        border-radius: var(--radius-sm);
        transition: all var(--transition-fast);
        display: block;
    }

    .option:hover:not(:disabled),
    .option.focused:not(:disabled) {
        background: var(--bg-hover);
    }

    .option.selected {
        background: var(--bg-accent-subtle);
        color: var(--text-accent);
        font-weight: 500;
    }

    .option.selected:hover:not(:disabled),
    .option.selected.focused:not(:disabled) {
        background: var(--bg-accent-subtle);
        filter: brightness(0.95);
    }

    .option:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .option:focus {
        outline: none;
    }

    .option.action-option {
        font-weight: 500;
        border-bottom: 1px solid var(--border-subtle);
    }
</style>
