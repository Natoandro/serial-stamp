<script lang="ts">
    import { specState } from "$lib/state/spec.svelte";
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { NumberInput } from "./forms";

    function markDirty() {
        workspaceState.isDirty = true;
    }

    function setGap(index: number, value: number) {
        const g = specState.current.layout.gap;
        let next: [number, number];
        if (typeof g === "number") {
            next = index === 0 ? [value, g] : [g, value];
        } else {
            next = index === 0 ? [value, g[1]] : [g[0], value];
        }
        specState.current.layout.gap = next;
        markDirty();
    }

    function setMargin4(index: number, value: number) {
        const m = specState.current.layout.margin;
        let curr: [number, number, number, number];
        if (typeof m === "number") curr = [m, m, m, m];
        else if (Array.isArray(m) && m.length === 2) curr = [m[0], m[1], m[0], m[1]];
        else if (Array.isArray(m) && m.length === 4) curr = [m[0], m[1], m[2], m[3]];
        else curr = [0, 0, 0, 0];

        const nextArr: [number, number, number, number] =
            index === 0
                ? [value, curr[1], curr[2], curr[3]]
                : index === 1
                  ? [curr[0], value, curr[2], curr[3]]
                  : index === 2
                    ? [curr[0], curr[1], value, curr[3]]
                    : [curr[0], curr[1], curr[2], value];

        specState.current.layout.margin = nextArr;
        markDirty();
    }
</script>

<div class="metrics-bar">
    <div class="group">
        <span class="label">Gap</span>
        <div class="inputs">
            <NumberInput
                step="0.5"
                title="Gap X"
                value={typeof specState.current.layout.gap === "number"
                    ? specState.current.layout.gap
                    : specState.current.layout.gap[0]}
                oninput={(e) => setGap(0, Number(e.currentTarget.value))}
            />
            <span class="x">×</span>
            <NumberInput
                step="0.5"
                title="Gap Y"
                value={typeof specState.current.layout.gap === "number"
                    ? specState.current.layout.gap
                    : specState.current.layout.gap[1]}
                oninput={(e) => setGap(1, Number(e.currentTarget.value))}
            />
        </div>
    </div>

    <div class="group">
        <span class="label">Margins</span>
        <div class="inputs margin-inputs">
            <NumberInput
                step="0.5"
                title="Top"
                value={Array.isArray(specState.current.layout.margin) && specState.current.layout.margin.length === 4
                    ? specState.current.layout.margin[0]
                    : 0}
                oninput={(e) => setMargin4(0, Number(e.currentTarget.value))}
            />
            <NumberInput
                step="0.5"
                title="Right"
                value={Array.isArray(specState.current.layout.margin) && specState.current.layout.margin.length === 4
                    ? specState.current.layout.margin[1]
                    : 0}
                oninput={(e) => setMargin4(1, Number(e.currentTarget.value))}
            />
            <NumberInput
                step="0.5"
                title="Bottom"
                value={Array.isArray(specState.current.layout.margin) && specState.current.layout.margin.length === 4
                    ? specState.current.layout.margin[2]
                    : 0}
                oninput={(e) => setMargin4(2, Number(e.currentTarget.value))}
            />
            <NumberInput
                step="0.5"
                title="Left"
                value={Array.isArray(specState.current.layout.margin) && specState.current.layout.margin.length === 4
                    ? specState.current.layout.margin[3]
                    : 0}
                oninput={(e) => setMargin4(3, Number(e.currentTarget.value))}
            />
        </div>
    </div>
</div>

<style>
    .metrics-bar {
        background: white;
        border-top: 1px solid #e5e7eb;
        padding: 0.75rem 1rem;
        display: flex;
        gap: 2rem;
        align-items: center;
        justify-content: center;
    }

    .group {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #4b5563;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .inputs {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .x {
        color: #9ca3af;
    }

    :global(.metrics-bar .number-input) {
        width: 60px;
        text-align: center;
    }
</style>
