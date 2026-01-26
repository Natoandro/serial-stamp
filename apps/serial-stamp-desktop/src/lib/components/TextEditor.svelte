<script lang="ts">
    import { specState, type TextSpec } from "$lib/state/spec.svelte";
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { resourceState } from "$lib/state/resources.svelte";

    function markDirty() {
        workspaceState.isDirty = true;
    }

    function addText() {
        const t: TextSpec = {
            template: "New Text",
            position: [10, 10],
            size: 24,
            color: "black",
        };
        specState.current.texts.push(t);
        markDirty();
    }

    function removeText(index: number) {
        specState.current.texts.splice(index, 1);
        markDirty();
    }

    function updateText(index: number, patch: Partial<TextSpec>) {
        const t = specState.current.texts[index];
        if (t) {
            Object.assign(t, patch);
            markDirty();
        }
    }
</script>

<div class="panel">
    <div class="header">
        <h3>Texts</h3>
        <button onclick={addText} class="primary-sm">+ Add Text</button>
    </div>

    {#if specState.current.texts.length === 0}
        <div class="empty-state">No texts defined. Add one to start.</div>
    {:else}
        <div class="list">
            {#each specState.current.texts as t, i (i)}
                <div class="text-card">
                    <div class="card-header">
                        <h4>Text #{i + 1}</h4>
                        <button class="icon-btn danger" onclick={() => removeText(i)}>×</button>
                    </div>

                    <div class="field-row full">
                        <label>
                            <span>Template</span>
                            <input
                                type="text"
                                value={t.template}
                                oninput={(e) => updateText(i, { template: e.currentTarget.value })}
                            />
                        </label>
                    </div>

                    <div class="field-row">
                        <label>
                            <span>Pos X</span>
                            <input
                                type="number"
                                step="0.5"
                                value={t.position[0]}
                                oninput={(e) => {
                                    const val = Number(e.currentTarget.value);
                                    updateText(i, { position: [val, t.position[1]] });
                                }}
                            />
                        </label>
                        <label>
                            <span>Pos Y</span>
                            <input
                                type="number"
                                step="0.5"
                                value={t.position[1]}
                                oninput={(e) => {
                                    const val = Number(e.currentTarget.value);
                                    updateText(i, { position: [t.position[0], val] });
                                }}
                            />
                        </label>
                    </div>

                    <div class="field-row three-col">
                        <label>
                            <span>Font</span>
                            <select
                                value={t.ttf ?? ""}
                                onchange={(e) => {
                                    const v = e.currentTarget.value;
                                    updateText(i, { ttf: v === "" ? undefined : v });
                                }}
                            >
                                <option value="">(Default)</option>
                                {#each resourceState.fonts as font}
                                    <option value={font}>{font}</option>
                                {/each}
                            </select>
                        </label>
                        <label>
                            <span>Size</span>
                            <input
                                type="number"
                                min="1"
                                step="1"
                                value={t.size}
                                oninput={(e) =>
                                    updateText(i, {
                                        size: Math.max(1, Math.trunc(Number(e.currentTarget.value))),
                                    })}
                            />
                        </label>
                        <label>
                            <span>Color</span>
                            <div class="color-row">
                                <input
                                    type="text"
                                    value={typeof t.color === "string" ? t.color : JSON.stringify(t.color)}
                                    oninput={(e) => updateText(i, { color: e.currentTarget.value })}
                                />
                                <input
                                    type="color"
                                    value={typeof t.color === "string" && t.color.startsWith("#") ? t.color : "#000000"}
                                    oninput={(e) => updateText(i, { color: e.currentTarget.value })}
                                />
                            </div>
                        </label>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .panel {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
    }

    h4 {
        margin: 0;
        font-size: 0.85rem;
        font-weight: 600;
        color: #4b5563;
    }

    button.primary-sm {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
    }

    button.primary-sm:hover {
        background: #1d4ed8;
    }

    .empty-state {
        text-align: center;
        color: #9ca3af;
        font-style: italic;
        padding: 1rem;
    }

    .list {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .text-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.25rem;
    }

    .icon-btn {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.1rem;
        line-height: 1;
        padding: 0 0.3rem;
        color: #9ca3af;
        border-radius: 4px;
    }

    .icon-btn.danger:hover {
        color: #dc2626;
        background: #fee2e2;
    }

    .field-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }

    .field-row.full {
        grid-template-columns: 1fr;
    }

    .field-row.three-col {
        grid-template-columns: 2fr 1fr 1fr;
    }

    label {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }

    label span {
        font-size: 0.75rem;
        color: #6b7280;
        font-weight: 500;
    }

    input,
    select {
        padding: 0.35rem;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        font-size: 0.85rem;
        width: 100%;
        box-sizing: border-box;
        background: white;
    }

    .color-row {
        display: flex;
        gap: 0.25rem;
        align-items: center;
        width: 100%;
    }

    .color-row input[type="text"] {
        flex: 1;
        min-width: 0;
    }

    .color-row input[type="color"] {
        width: 28px;
        height: 28px;
        padding: 1px;
        cursor: pointer;
        flex-shrink: 0;
    }
</style>
