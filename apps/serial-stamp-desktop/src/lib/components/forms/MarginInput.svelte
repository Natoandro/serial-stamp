<script lang="ts">
    import NumberInput from "./NumberInput.svelte";
    import SegmentedControl from "./SegmentedControl.svelte";

    interface Props {
        value: number | [number, number] | [number, number, number, number];
        oninput?: (value: number | [number, number] | [number, number, number, number]) => void;
        id?: string;
        label?: string;
        size?: "compact" | "default" | "comfortable";
    }

    let { value = $bindable(0), oninput, id, label, size = "default" }: Props = $props();

    type MarginMode = "uniform" | "symmetric" | "individual";

    const modeOptions = [
        { value: "uniform", label: "Uniform" },
        { value: "symmetric", label: "Symmetric" },
        { value: "individual", label: "Individual" },
    ];

    let mode = $state<MarginMode>("uniform");
    let uniformValue = $state(0);
    let verticalValue = $state(0);
    let horizontalValue = $state(0);
    let topValue = $state(0);
    let rightValue = $state(0);
    let bottomValue = $state(0);
    let leftValue = $state(0);

    function initializeFromValue(val: number | [number, number] | [number, number, number, number]) {
        if (typeof val === "number") {
            mode = "uniform";
            uniformValue = val;
            verticalValue = val;
            horizontalValue = val;
            topValue = val;
            rightValue = val;
            bottomValue = val;
            leftValue = val;
        } else if (val.length === 2) {
            mode = "symmetric";
            verticalValue = val[0];
            horizontalValue = val[1];
            uniformValue = val[0];
            topValue = val[0];
            rightValue = val[1];
            bottomValue = val[0];
            leftValue = val[1];
        } else {
            mode = "individual";
            topValue = val[0];
            rightValue = val[1];
            bottomValue = val[2];
            leftValue = val[3];
            uniformValue = val[0];
            verticalValue = val[0];
            horizontalValue = val[1];
        }
    }

    function handleModeChange(newMode: string) {
        mode = newMode as MarginMode;

        if (newMode === "uniform") {
            oninput?.(uniformValue);
        } else if (newMode === "symmetric") {
            oninput?.([verticalValue, horizontalValue]);
        } else {
            oninput?.([topValue, rightValue, bottomValue, leftValue]);
        }
    }

    function handleUniformChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        uniformValue = newValue;
        oninput?.(newValue);
    }

    function handleVerticalChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        verticalValue = newValue;
        oninput?.([newValue, horizontalValue]);
    }

    function handleHorizontalChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        horizontalValue = newValue;
        oninput?.([verticalValue, newValue]);
    }

    function handleTopChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        topValue = newValue;
        oninput?.([newValue, rightValue, bottomValue, leftValue]);
    }

    function handleRightChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        rightValue = newValue;
        oninput?.([topValue, newValue, bottomValue, leftValue]);
    }

    function handleBottomChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        bottomValue = newValue;
        oninput?.([topValue, rightValue, newValue, leftValue]);
    }

    function handleLeftChange(e: Event) {
        const target = e.currentTarget as HTMLInputElement;
        const newValue = Number(target.value);
        leftValue = newValue;
        oninput?.([topValue, rightValue, bottomValue, newValue]);
    }

    $effect(() => {
        initializeFromValue(value);
    });
</script>

<div class="margin-input">
    {#if label}
        <div class="header-row">
            <label for={id}>{label}</label>
            <SegmentedControl options={modeOptions} value={mode} onchange={handleModeChange} size="compact" />
        </div>
    {:else}
        <SegmentedControl options={modeOptions} value={mode} onchange={handleModeChange} size="compact" />
    {/if}

    <div class="inputs">
        {#if mode === "uniform"}
            <NumberInput {id} value={uniformValue} oninput={handleUniformChange} min={0} step={1} {size} />
        {:else if mode === "symmetric"}
            <div class="split-inputs">
                <div class="input-group">
                    <label for="{id}-vertical">Vertical</label>
                    <NumberInput
                        id="{id}-vertical"
                        value={verticalValue}
                        oninput={handleVerticalChange}
                        min={0}
                        step={1}
                        {size}
                    />
                </div>
                <div class="input-group">
                    <label for="{id}-horizontal">Horizontal</label>
                    <NumberInput
                        id="{id}-horizontal"
                        value={horizontalValue}
                        oninput={handleHorizontalChange}
                        min={0}
                        step={1}
                        {size}
                    />
                </div>
            </div>
        {:else}
            <div class="grid-inputs">
                <div class="input-group">
                    <label for="{id}-top">Top</label>
                    <NumberInput id="{id}-top" value={topValue} oninput={handleTopChange} min={0} step={1} {size} />
                </div>
                <div class="input-group">
                    <label for="{id}-right">Right</label>
                    <NumberInput
                        id="{id}-right"
                        value={rightValue}
                        oninput={handleRightChange}
                        min={0}
                        step={1}
                        {size}
                    />
                </div>
                <div class="input-group">
                    <label for="{id}-bottom">Bottom</label>
                    <NumberInput
                        id="{id}-bottom"
                        value={bottomValue}
                        oninput={handleBottomChange}
                        min={0}
                        step={1}
                        {size}
                    />
                </div>
                <div class="input-group">
                    <label for="{id}-left">Left</label>
                    <NumberInput id="{id}-left" value={leftValue} oninput={handleLeftChange} min={0} step={1} {size} />
                </div>
            </div>
        {/if}
    </div>
</div>

<style>
    .margin-input {
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
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary);
        white-space: nowrap;
        margin: 0;
        letter-spacing: -0.01em;
    }

    .inputs {
        display: flex;
        flex-direction: column;
    }

    .split-inputs {
        display: flex;
        gap: 0.5rem;
    }

    .grid-inputs {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
    }

    .input-group {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .input-group label {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
    }
</style>
