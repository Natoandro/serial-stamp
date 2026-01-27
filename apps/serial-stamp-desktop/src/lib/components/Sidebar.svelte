<script lang="ts">
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { resourceState } from "$lib/state/resources.svelte";
    import { specState } from "$lib/state/spec.svelte";
    import TextEditor from "./TextEditor.svelte";
    import AccordionGroup from "./AccordionGroup.svelte";
    import AccordionSection from "./AccordionSection.svelte";
    import { Input, NumberInput, Select, ColorInput, Button, IconButton, GridSizePicker } from "./forms";

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
            <Button variant="primary" onclick={newWorkspace} class="full-width">Create New Project</Button>
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
                                <NumberInput
                                    id="stack-size"
                                    min={1}
                                    step={1}
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
                                <Select
                                    id="source-image"
                                    value={specState.current["source-image"]}
                                    onchange={(e) => {
                                        specState.current["source-image"] = e.currentTarget.value;
                                        markDirty();
                                    }}
                                >
                                    {#snippet children()}
                                        <option value="">(None)</option>
                                        {#each resourceState.images as img}
                                            <option value={img}>{img}</option>
                                        {/each}
                                    {/snippet}
                                </Select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="bg-color">Background</label>
                            <ColorInput
                                id="bg-color"
                                value={typeof specState.current.background === "string"
                                    ? specState.current.background
                                    : JSON.stringify(specState.current.background)}
                                oninput={(e) => {
                                    specState.current.background = e.currentTarget.value;
                                    markDirty();
                                }}
                            />
                        </div>

                        <div class="form-group">
                            <label for="grid-size">Grid Size</label>
                            <GridSizePicker
                                value={specState.current.layout["grid-size"]}
                                onchange={(size) => {
                                    specState.current.layout["grid-size"] = size;
                                    markDirty();
                                }}
                            />
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
                            <IconButton onclick={importImage} title="Import Image" ariaLabel="Import Image"
                                >+</IconButton
                            >
                        </div>
                        <ul class="resource-list">
                            {#each resourceState.images as img}
                                <li>
                                    <span class="name" title={img}>{img.split("/").pop()}</span>
                                    <IconButton
                                        variant="danger"
                                        onclick={() => removeFile("images", img)}
                                        ariaLabel="Remove image">×</IconButton
                                    >
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
                            <IconButton onclick={importFont} title="Import Font" ariaLabel="Import Font">+</IconButton>
                        </div>
                        <ul class="resource-list">
                            {#each resourceState.fonts as font}
                                <li>
                                    <span class="name" title={font}>{font.split("/").pop()}</span>
                                    <IconButton
                                        variant="danger"
                                        onclick={() => removeFile("fonts", font)}
                                        ariaLabel="Remove font">×</IconButton
                                    >
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

    label {
        font-size: 0.8rem;
        font-weight: 500;
        color: var(--text-primary);
        white-space: nowrap;
    }

    .header-row-inline {
        display: flex;
        justify-content: flex-end;
        align-items: center;
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

    :global(.full-width) {
        width: 100%;
    }
</style>
