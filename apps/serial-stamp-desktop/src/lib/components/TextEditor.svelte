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

<div class="header-row-inline">
    <button onclick={addText} class="icon-btn" title="Add Text">+</button>
</div>

{#if specState.current.texts.length === 0}
    <div class="empty-state">No texts defined.</div>
{:else}
    <div class="list">
        {#each specState.current.texts as t, i (i)}
            <div class="text-card">
                <div class="card-header">
                    <h4>#{i + 1}</h4>
                    <button class="icon-btn danger" onclick={() => removeText(i)}>×</button>
                </div>

                <div class="form-group">
                    <input
                        type="text"
                        placeholder="Template text"
                        value={t.template}
                        oninput={(e) => updateText(i, { template: e.currentTarget.value })}
                        aria-label="Template text"
                    />
                </div>

                <div class="row">
                    <div class="form-group half">
                        <label for="text-{i}-x" class="sub-label">X</label>
                        <input
                            id="text-{i}-x"
                            type="number"
                            step="0.5"
                            value={t.position[0]}
                            oninput={(e) => {
                                const val = Number(e.currentTarget.value);
                                updateText(i, { position: [val, t.position[1]] });
                            }}
                        />
                    </div>
                    <div class="form-group half">
                        <label for="text-{i}-y" class="sub-label">Y</label>
                        <input
                            id="text-{i}-y"
                            type="number"
                            step="0.5"
                            value={t.position[1]}
                            oninput={(e) => {
                                const val = Number(e.currentTarget.value);
                                updateText(i, { position: [t.position[0], val] });
                            }}
                        />
                    </div>
                </div>

                <div class="row">
                    <div class="form-group grow">
                        <select
                            value={t.ttf ?? ""}
                            onchange={(e) => {
                                const v = e.currentTarget.value;
                                updateText(i, { ttf: v === "" ? undefined : v });
                            }}
                            aria-label="Font"
                        >
                            <option value="">(Default Font)</option>
                            {#each resourceState.fonts as font}
                                <option value={font}>{font.split("/").pop()}</option>
                            {/each}
                        </select>
                    </div>
                    <div class="form-group narrow">
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={t.size}
                            title="Font Size"
                            aria-label="Font Size"
                            oninput={(e) =>
                                updateText(i, {
                                    size: Math.max(1, Math.trunc(Number(e.currentTarget.value))),
                                })}
                        />
                    </div>
                </div>

                <div class="color-row">
                    <input
                        type="text"
                        value={typeof t.color === "string" ? t.color : JSON.stringify(t.color)}
                        oninput={(e) => updateText(i, { color: e.currentTarget.value })}
                        aria-label="Color Text"
                    />
                    <input
                        type="color"
                        value={typeof t.color === "string" && t.color.startsWith("#") ? t.color : "#000000"}
                        oninput={(e) => updateText(i, { color: e.currentTarget.value })}
                        aria-label="Color Picker"
                    />
                </div>
            </div>
        {/each}
    </div>
{/if}

<style>
    .header-row-inline {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        margin-bottom: var(--space-2);
    }

    h4 {
        margin: 0;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-tertiary);
    }

    .icon-btn {
        padding: 0;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        background: none;
        cursor: pointer;
        font-weight: bold;
        color: var(--icon-primary);
        border-radius: var(--radius-sm);
        transition: all var(--transition-fast);
    }

    .icon-btn:hover {
        background: var(--bg-hover);
        color: var(--icon-hover);
    }

    .icon-btn.danger:hover {
        color: var(--state-error);
        background: oklch(from var(--state-error) l c h / 0.1);
    }

    .empty-state {
        text-align: center;
        color: var(--text-tertiary);
        font-style: italic;
        font-size: 0.85rem;
    }

    .list {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
    }

    .text-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: var(--space-3);
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        box-shadow: var(--shadow-sm);
        transition: border-color var(--transition-fast);
    }

    .text-card:hover {
        border-color: var(--border-normal);
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .form-group {
        display: flex;
        flex-direction: column;
    }

    .row {
        display: flex;
        gap: var(--space-2);
        align-items: flex-end;
    }

    .half {
        flex: 1;
    }

    .grow {
        flex-grow: 1;
    }

    .narrow {
        width: 50px;
        flex-shrink: 0;
    }

    .sub-label {
        font-size: 0.7rem;
        color: var(--text-secondary);
        margin-bottom: 2px;
    }

    input,
    select {
        padding: 0.35rem;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-sm);
        font-size: 0.85rem;
        width: 100%;
        box-sizing: border-box;
        background: var(--input-bg);
        color: var(--input-text);
        transition: border-color var(--transition-fast);
    }

    input:hover,
    select:hover {
        border-color: var(--input-border-hover);
    }

    input:focus,
    select:focus {
        outline: none;
        border-color: var(--input-border-focus);
        box-shadow: 0 0 0 2px var(--bg-accent-subtle);
    }

    .color-row {
        display: flex;
        gap: var(--space-1);
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
        border: none;
        background: none;
    }
</style>
