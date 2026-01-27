<script lang="ts">
    interface Props {
        value: [number, number];
        onchange?: (size: [number, number]) => void;
        maxCols?: number;
        maxRows?: number;
        disabled?: boolean;
        class?: string;
    }

    let {
        value = $bindable([1, 1]),
        onchange,
        maxCols = 10,
        maxRows = 10,
        disabled = false,
        class: className = "",
    }: Props = $props();

    let hoverX = $state(0);
    let hoverY = $state(0);
    let isHovering = $state(false);

    function handleCellHover(x: number, y: number) {
        if (disabled) return;
        hoverX = x;
        hoverY = y;
        isHovering = true;
    }

    function handleMouseLeave() {
        isHovering = false;
    }

    function handleClick() {
        if (disabled || !isHovering) return;
        const newSize: [number, number] = [hoverX, hoverY];
        value = newSize;
        if (onchange) {
            onchange(newSize);
        }
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (disabled) return;
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            handleClick();
        }
    }

    // Display text showing current selection
    let displayText = $derived(isHovering ? `${hoverX} × ${hoverY}` : `${value[0]} × ${value[1]}`);
</script>

<div class="grid-selector {className}" class:disabled>
    <div class="label">{displayText}</div>
    <div
        class="grid-container"
        onmouseleave={handleMouseLeave}
        onclick={handleClick}
        onkeydown={handleKeyDown}
        role="button"
        tabindex={disabled ? -1 : 0}
        aria-label="Grid size selector"
    >
        {#each Array(maxRows) as _, rowIndex}
            {#each Array(maxCols) as _, colIndex}
                {@const x = colIndex + 1}
                {@const y = rowIndex + 1}
                {@const isSelected = x <= value[0] && y <= value[1]}
                {@const isHovered = isHovering && x <= hoverX && y <= hoverY}
                <div
                    class="grid-cell"
                    class:selected={isSelected}
                    class:hovered={isHovered}
                    onmouseenter={() => handleCellHover(x, y)}
                    role="presentation"
                ></div>
            {/each}
        {/each}
    </div>
</div>

<style>
    .grid-selector {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        width: fit-content;
    }

    .grid-selector.disabled {
        opacity: 0.6;
        pointer-events: none;
    }

    .label {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-primary);
        text-align: center;
        min-height: 1.2rem;
    }

    .grid-container {
        display: grid;
        grid-template-columns: repeat(var(--max-cols, 10), 1fr);
        gap: 2px;
        padding: 0.5rem;
        background: var(--bg-primary);
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: border-color var(--transition-fast);
    }

    .grid-container:hover:not(.disabled) {
        border-color: var(--input-border-hover);
    }

    .grid-container:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .grid-cell {
        width: 16px;
        height: 16px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: 2px;
        transition: all var(--transition-fast);
    }

    .grid-cell:hover {
        background: var(--color-accent-100);
        border-color: var(--color-accent-300);
    }

    .grid-cell.selected {
        background: repeating-linear-gradient(
            45deg,
            var(--color-accent-200),
            var(--color-accent-200) 4px,
            var(--color-accent-300) 4px,
            var(--color-accent-300) 8px
        );
        border-color: var(--color-accent-300);
    }

    .grid-cell.hovered {
        background: var(--color-accent-400);
        border-color: var(--color-accent-500);
    }

    .grid-cell.selected.hovered {
        background: repeating-linear-gradient(
            45deg,
            var(--color-accent-400),
            var(--color-accent-400) 4px,
            var(--color-accent-500) 4px,
            var(--color-accent-500) 8px
        );
        border-color: var(--color-accent-500);
    }

    .grid-cell.hovered:hover {
        background: var(--color-accent-500);
        border-color: var(--color-accent-600);
    }
</style>
