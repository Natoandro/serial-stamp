<script lang="ts">
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { resourceState } from "$lib/state/resources.svelte";
    import { specState } from "$lib/state/spec.svelte";
    import TextEditor from "./TextEditor.svelte";
    import AccordionGroup from "./AccordionGroup.svelte";
    import AccordionSection from "./AccordionSection.svelte";

    let { newWorkspace } = $props<{ newWorkspace: () => void }>();

    function markDirty() {
        workspaceState.isDirty = true;
    }

    async function importImage() {
        if (workspaceState.currentWorkspaceId) {
            await resourceState.importImage(workspaceState.currentWorkspaceId);
        }
    }

    async function importFont() {
        if (workspaceState.currentWorkspaceId) {
            await resourceState.importFont(workspaceState.currentWorkspaceId);
        }
    }

    async function removeFile(category: "images" | "fonts", filename: string) {
        if (workspaceState.currentWorkspaceId) {
            if (confirm(`Delete ${filename}?`)) {
                await resourceState.remove(workspaceState.currentWorkspaceId, category, filename);
            }
        }
    }
</script>

<aside class="sidebar">
    <div class="section project-info">
        <h2>Project</h2>
        {#if workspaceState.currentWorkspaceId}
            <div class="kv">
                <span class="label">ID</span>
                <span class="value" title={workspaceState.currentWorkspaceId}
                    >{workspaceState.currentWorkspaceId.slice(0, 8)}...</span
                >
            </div>
            <div class="kv">
                <span class="label">File</span>
                <span class="value" title={workspaceState.currentFilePath ?? "Unsaved"}
                    >{workspaceState.currentFilePath
                        ? workspaceState.currentFilePath.split(/[/\\]/).pop()
                        : "Unsaved"}</span
                >
            </div>
        {:else}
            <button onclick={newWorkspace} class="primary full-width">Create New Project</button>
        {/if}
    </div>

    {#if workspaceState.currentWorkspaceId}
        <AccordionGroup storageKey="sidebar-accordion" defaultExpanded="global">
            {#snippet children({
                isExpanded,
                toggle,
            }: {
                isExpanded: (id: string) => boolean;
                toggle: (id: string) => void;
            })}
                <AccordionSection
                    title="Global Settings"
                    expanded={isExpanded("global")}
                    onclick={() => toggle("global")}
                >
                    {#snippet children()}
                        <div class="row">
                            <div class="form-group half">
                                <label for="stack-size">Stack Size</label>
                                <input
                                    id="stack-size"
                                    type="number"
                                    min="1"
                                    step="1"
                                    value={specState.current["stack-size"]}
                                    oninput={(e) => {
                                        specState.current["stack-size"] = Math.max(
                                            1,
                                            Math.trunc(Number(e.currentTarget.value)),
                                        );
                                        markDirty();
                                    }}
                                />
                            </div>
                            <div class="form-group half">
                                <label for="source-image">Source Image</label>
                                <select
                                    id="source-image"
                                    value={specState.current["source-image"]}
                                    onchange={(e) => {
                                        specState.current["source-image"] = e.currentTarget.value;
                                        markDirty();
                                    }}
                                >
                                    <option value="">(None)</option>
                                    {#each resourceState.images as img}
                                        <option value={img}>{img}</option>
                                    {/each}
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="bg-color">Background</label>
                            <div class="color-row">
                                <input
                                    id="bg-color"
                                    type="text"
                                    value={typeof specState.current.background === "string"
                                        ? specState.current.background
                                        : JSON.stringify(specState.current.background)}
                                    oninput={(e) => {
                                        specState.current.background = e.currentTarget.value;
                                        markDirty();
                                    }}
                                />
                                <input
                                    type="color"
                                    value={typeof specState.current.background === "string" &&
                                    specState.current.background.startsWith("#")
                                        ? specState.current.background
                                        : "#ffffff"}
                                    oninput={(e) => {
                                        specState.current.background = e.currentTarget.value;
                                        markDirty();
                                    }}
                                />
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="grid-size-x">Grid Size (X / Y)</label>
                            <div class="row">
                                <input
                                    id="grid-size-x"
                                    type="number"
                                    min="1"
                                    step="1"
                                    placeholder="X"
                                    value={specState.current.layout["grid-size"][0]}
                                    oninput={(e) => {
                                        specState.current.layout["grid-size"][0] = Math.max(
                                            1,
                                            Math.trunc(Number(e.currentTarget.value)),
                                        );
                                        markDirty();
                                    }}
                                />
                                <input
                                    type="number"
                                    min="1"
                                    step="1"
                                    placeholder="Y"
                                    value={specState.current.layout["grid-size"][1]}
                                    oninput={(e) => {
                                        specState.current.layout["grid-size"][1] = Math.max(
                                            1,
                                            Math.trunc(Number(e.currentTarget.value)),
                                        );
                                        markDirty();
                                    }}
                                />
                            </div>
                        </div>
                    {/snippet}
                </AccordionSection>

                <AccordionSection title="Texts" expanded={isExpanded("texts")} onclick={() => toggle("texts")}>
                    {#snippet children()}
                        <TextEditor />
                    {/snippet}
                </AccordionSection>

                <AccordionSection title="Images" expanded={isExpanded("images")} onclick={() => toggle("images")}>
                    {#snippet children()}
                        <div class="header-row-inline">
                            <button class="icon-btn" onclick={importImage} title="Import Image">+</button>
                        </div>
                        <ul class="resource-list">
                            {#each resourceState.images as img}
                                <li>
                                    <span class="name" title={img}>{img.split("/").pop()}</span>
                                    <button class="icon-btn danger" onclick={() => removeFile("images", img)}>×</button>
                                </li>
                            {:else}
                                <li class="empty">No images</li>
                            {/each}
                        </ul>
                    {/snippet}
                </AccordionSection>

                <AccordionSection title="Fonts" expanded={isExpanded("fonts")} onclick={() => toggle("fonts")}>
                    {#snippet children()}
                        <div class="header-row-inline">
                            <button class="icon-btn" onclick={importFont} title="Import Font">+</button>
                        </div>
                        <ul class="resource-list">
                            {#each resourceState.fonts as font}
                                <li>
                                    <span class="name" title={font}>{font.split("/").pop()}</span>
                                    <button class="icon-btn danger" onclick={() => removeFile("fonts", font)}>×</button>
                                </li>
                            {:else}
                                <li class="empty">No fonts</li>
                            {/each}
                        </ul>
                    {/snippet}
                </AccordionSection>
            {/snippet}
        </AccordionGroup>
    {/if}
</aside>

<style>
    .sidebar {
        width: 320px;
        background: var(--sidebar-bg);
        border-right: 1px solid var(--sidebar-border);
        display: flex;
        flex-direction: column;
        height: 100%;
        overflow: hidden;
        padding: var(--space-4);
        gap: 0;
    }

    .section {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        flex-shrink: 0;
    }

    .project-info {
        margin-bottom: var(--space-4);
        padding-bottom: var(--space-4);
        border-bottom: 2px solid var(--border-strong);
    }

    .project-info h2 {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--sidebar-header-text);
        font-weight: 600;
        margin: 0;
    }

    .kv {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
    }

    .kv .label {
        color: var(--text-secondary);
    }

    .kv .value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 150px;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .row {
        display: flex;
        gap: 0.5rem;
    }

    .half {
        flex: 1;
        min-width: 0;
    }

    .color-row {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }

    .color-row input[type="text"] {
        flex: 1;
    }

    .color-row input[type="color"] {
        width: 34px;
        height: 34px;
        padding: 2px;
        cursor: pointer;
    }

    label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-primary);
        white-space: nowrap;
    }

    input,
    select {
        padding: 0.4rem;
        border: 1px solid var(--input-border);
        border-radius: var(--radius-md);
        font-size: 0.9rem;
        background: var(--input-bg);
        color: var(--input-text);
        width: 100%;
        box-sizing: border-box;
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
        box-shadow: 0 0 0 3px var(--bg-accent-subtle);
    }

    .header-row-inline {
        display: flex;
        justify-content: flex-end;
        align-items: center;
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

    .resource-list {
        list-style: none;
        padding: 0;
        margin: 0;
        background: var(--bg-primary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    .resource-list li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 0.5rem;
        font-size: 0.85rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    .resource-list li:last-child {
        border-bottom: none;
    }

    .resource-list li.empty {
        color: var(--text-tertiary);
        font-style: italic;
        justify-content: center;
    }

    .name {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
    }

    button.primary {
        background: var(--button-primary-bg);
        color: var(--button-primary-text);
        border: none;
        padding: 0.5rem;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-size: 0.9rem;
        transition: background-color var(--transition-fast);
    }

    button.primary:hover {
        background: var(--button-primary-bg-hover);
    }

    .full-width {
        width: 100%;
    }
</style>
