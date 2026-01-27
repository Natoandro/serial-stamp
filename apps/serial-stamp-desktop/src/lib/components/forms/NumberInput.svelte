<script lang="ts">
    interface Props {
        value: number;
        oninput?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        onchange?: (e: Event & { currentTarget: HTMLInputElement }) => void;
        onkeydown?: (e: KeyboardEvent) => void;
        min?: number;
        max?: number;
        step?: number | string;
        placeholder?: string;
        id?: string;
        disabled?: boolean;
        readonly?: boolean;
        size?: "compact" | "default" | "comfortable";
        class?: string;
        ariaLabel?: string;
        title?: string;
    }

    let {
        value = $bindable(0),
        oninput,
        onchange,
        onkeydown,
        min,
        max,
        step = 1,
        placeholder,
        id,
        disabled = false,
        readonly = false,
        size = "default",
        class: className = "",
        ariaLabel,
        title,
    }: Props = $props();

    let inputElement: HTMLInputElement | undefined = $state();

    function increment() {
        if (disabled || readonly) return;
        const stepValue = typeof step === "string" ? parseFloat(step) : step;
        const newValue = value + stepValue;
        if (max === undefined || newValue <= max) {
            value = newValue;
            triggerInput();
        }
    }

    function decrement() {
        if (disabled || readonly) return;
        const stepValue = typeof step === "string" ? parseFloat(step) : step;
        const newValue = value - stepValue;
        if (min === undefined || newValue >= min) {
            value = newValue;
            triggerInput();
        }
    }

    function triggerInput() {
        if (inputElement && oninput) {
            const event = new Event("input", { bubbles: true });
            Object.defineProperty(event, "currentTarget", { value: inputElement });
            oninput(event as Event & { currentTarget: HTMLInputElement });
        }
    }

    function handleWheel(e: WheelEvent) {
        if (disabled || readonly || document.activeElement !== inputElement) return;
        e.preventDefault();
        if (e.deltaY < 0) {
            increment();
        } else if (e.deltaY > 0) {
            decrement();
        }
    }
</script>

<div class="number-input-wrapper {size} {className}" class:disabled class:readonly>
    <input
        bind:this={inputElement}
        {id}
        type="number"
        {value}
        {min}
        {max}
        {step}
        {placeholder}
        {disabled}
        {readonly}
        {title}
        {oninput}
        {onchange}
        {onkeydown}
        onwheel={handleWheel}
        class="number-input"
        aria-label={ariaLabel}
    />
    <div class="spinners">
        <button
            type="button"
            class="spinner-btn increment"
            onclick={increment}
            disabled={disabled || readonly || (max !== undefined && value >= max)}
            tabindex="-1"
            aria-label="Increment"
        >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M6 3L9 7L3 7L6 3Z" fill="currentColor" />
            </svg>
        </button>
        <button
            type="button"
            class="spinner-btn decrement"
            onclick={decrement}
            disabled={disabled || readonly || (min !== undefined && value <= min)}
            tabindex="-1"
            aria-label="Decrement"
        >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M6 9L3 5L9 5L6 9Z" fill="currentColor" />
            </svg>
        </button>
    </div>
</div>

<style>
    .number-input-wrapper {
        position: relative;
        display: flex;
        align-items: center;
        width: 100%;
    }

    .number-input {
        padding: 0 2rem 0 0.5rem;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        font-size: 0.9rem;
        background: var(--input-bg);
        color: var(--input-text);
        width: 100%;
        box-sizing: border-box;
        transition: border-color var(--transition-fast);
    }

    /* Hide default spinner */
    .number-input::-webkit-inner-spin-button,
    .number-input::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    .number-input[type="number"] {
        -moz-appearance: textfield;
        appearance: textfield;
    }

    .number-input-wrapper.compact .number-input {
        height: var(--input-height-compact);
        font-size: 0.85rem;
    }

    .number-input-wrapper.default .number-input {
        height: var(--input-height-default);
    }

    .number-input-wrapper.comfortable .number-input {
        height: var(--input-height-comfortable);
        font-size: 0.95rem;
    }

    .number-input:hover:not(:disabled) {
        border-color: var(--input-border-hover);
    }

    .number-input:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .number-input:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .number-input:read-only {
        background: var(--bg-secondary);
    }

    .spinners {
        position: absolute;
        right: 2px;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        flex-direction: column;
        gap: 1px;
    }

    .spinner-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: calc(50% - 2px);
        padding: 0;
        margin: 0;
        border: none;
        background: transparent;
        color: var(--text-secondary);
        cursor: pointer;
        border-radius: 3px;
        transition: all 0.12s ease;
    }

    .number-input-wrapper.compact .spinner-btn {
        width: 18px;
    }

    .number-input-wrapper.comfortable .spinner-btn {
        width: 22px;
    }

    .spinner-btn:hover:not(:disabled) {
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }

    .spinner-btn:active:not(:disabled) {
        background: var(--bg-secondary);
    }

    .spinner-btn:disabled {
        opacity: 0.3;
        cursor: not-allowed;
    }

    .spinner-btn svg {
        width: 10px;
        height: 10px;
        pointer-events: none;
    }

    .number-input-wrapper.compact .spinner-btn svg {
        width: 8px;
        height: 8px;
    }

    .number-input-wrapper.comfortable .spinner-btn svg {
        width: 11px;
        height: 11px;
    }

    .number-input-wrapper.disabled .spinners,
    .number-input-wrapper.readonly .spinners {
        pointer-events: none;
        opacity: 0.6;
    }
</style>
