<script lang="ts">
    interface Props {
        checked: boolean;
        onchange?: (checked: boolean) => void;
        disabled?: boolean;
        label?: string;
        id?: string;
        class?: string;
        size?: "compact" | "default";
        ariaLabel?: string;
    }

    let {
        checked = $bindable(false),
        onchange,
        disabled = false,
        label,
        id,
        class: className = "",
        size = "default",
        ariaLabel,
    }: Props = $props();

    function handleToggle() {
        if (disabled) return;
        checked = !checked;
        if (onchange) {
            onchange(checked);
        }
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (disabled) return;
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            handleToggle();
        }
    }
</script>

<div class="switch-container {className}">
    {#if label}
        <label for={id} class="switch-label">{label}</label>
    {/if}
    <button
        {id}
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={ariaLabel ?? label}
        class="switch {size}"
        class:checked
        {disabled}
        onclick={handleToggle}
        onkeydown={handleKeyDown}
        tabindex={disabled ? -1 : 0}
    >
        <span class="switch-thumb"></span>
    </button>
</div>

<style>
    .switch-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .switch-label {
        font-size: 0.85rem;
        color: var(--text-primary);
        cursor: pointer;
        user-select: none;
    }

    .switch {
        position: relative;
        border: none;
        border-radius: var(--radius-full);
        background: var(--color-neutral-300);
        cursor: pointer;
        transition: background-color var(--transition-fast);
        padding: 0;
        flex-shrink: 0;
    }

    .switch.default {
        width: 42px;
        height: 24px;
    }

    .switch.compact {
        width: 36px;
        height: 20px;
    }

    .switch:hover:not(:disabled) {
        background: var(--color-neutral-400);
    }

    .switch:focus {
        outline: none;
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .switch:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .switch.checked {
        background: var(--color-accent-500);
    }

    .switch.checked:hover:not(:disabled) {
        background: var(--color-accent-600);
    }

    .switch-thumb {
        position: absolute;
        top: 2px;
        left: 2px;
        background: white;
        border-radius: var(--radius-full);
        transition: transform var(--transition-fast);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }

    .switch.default .switch-thumb {
        width: 20px;
        height: 20px;
    }

    .switch.compact .switch-thumb {
        width: 16px;
        height: 16px;
    }

    .switch.default.checked .switch-thumb {
        transform: translateX(18px);
    }

    .switch.compact.checked .switch-thumb {
        transform: translateX(16px);
    }
</style>
