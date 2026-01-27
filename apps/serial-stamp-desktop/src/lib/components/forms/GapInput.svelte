<script lang="ts">
    import NumberInput from "./NumberInput.svelte";
    import SegmentedControl from "./SegmentedControl.svelte";

    interface Props {
        value: number | [number, number];
        oninput?: (value: number | [number, number]) => void;
        id?: string;
        label?: string;
        size?: "compact" | "default" | "comfortable";
    }

    let { value = $bindable(0), oninput, id, label, size = "default" }: Props = $props();

    let mode = $state<"uniform" | "split">(typeof value === "number" ? "uniform" : "split");
    let uniformValue = $state(typeof value === "number" ? value : value[0]);
    let xValue = $state(typeof value === "number" ? value : value[0]);
    let yValue = $state(typeof value === "number" ? value : value[1]);

    const modeOptions = [
        { value: "uniform", label: "Uniform" },
        { value: "split", label: "Split" },
    ];

    function handleModeChange(newMode: string) {
        mode = newMode as "uniform" | "split";
        if (mode === "uniform") {
            const newValue = xValue;
            uniformValue = newValue;
            oninput?.(newValue);
        } else {
            const newValue: [number, number] = [uniformValue, uniformValue];
            xValue = uniformValue;
            yValue = uniformValue;
            oninput?.(newValue);
        }
    }

    function handleUniformChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        uniformValue = newValue;
        oninput?.(newValue);
    }

    function handleXChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        xValue = newValue;
        oninput?.([newValue, yValue]);
    }

    function handleYChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        yValue = newValue;
        oninput?.([xValue, newValue]);
    }

    $effect(() => {
        if (typeof value === "number") {
            mode = "uniform";
            uniformValue = value;
        } else {
            mode = "split";
            xValue = value[0];
            yValue = value[1];
        }
    });
</script>

<div class="gap-input">
    {#if label}
        <div class="header-row">
            <label for={id}>{label}</label>
            <SegmentedControl options={modeOptions} value={mode} onchange={handleModeChange} size="compact" />
        </div>
    {:else}
        <SegmentedControl options={modeOptions} value={mode} onchange={handleModeChange} size="compact" />
    {/if}

    {#if mode === "uniform"}
        <div class="labeled-input">
            <span class="input-label">All</span>
            <NumberInput {id} value={uniformValue} oninput={handleUniformChange} min={0} step={1} {size} />
        </div>
    {:else}
        <div class="split-inputs">
            <div class="labeled-input">
                <span class="input-label">X</span>
                <NumberInput id="{id}-x" value={xValue} oninput={handleXChange} min={0} step={1} {size} />
            </div>
            <div class="labeled-input">
                <span class="input-label">Y</span>
                <NumberInput id="{id}-y" value={yValue} oninput={handleYChange} min={0} step={1} {size} />
            </div>
        </div>
    {/if}
</div>

<style>
    .gap-input {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        margin-bottom: 0.25rem;
    }

    .header-row label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-primary);
        white-space: nowrap;
        margin: 0;
    }

    .split-inputs {
        display: flex;
        gap: 0.5rem;
    }

    .labeled-input {
        flex: 1;
        position: relative;
        display: flex;
        align-items: center;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        background: var(--input-bg);
        transition: border-color var(--transition-fast);
    }

    .labeled-input:hover {
        border-color: var(--input-border-hover);
    }

    .labeled-input:focus-within {
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .input-label {
        padding: 0 0.5rem 0 0.75rem;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
        height: 100%;
        display: flex;
        align-items: center;
        user-select: none;
        flex-shrink: 0;
    }

    .labeled-input :global(.number-input-wrapper) {
        flex: 1;
    }

    .labeled-input :global(.number-input) {
        border: none;
        background: transparent;
        padding-left: 0.5rem;
        text-align: right;
    }

    .labeled-input :global(.number-input:focus) {
        border: none;
        box-shadow: none;
    }
</style>
