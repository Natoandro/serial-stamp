<script lang="ts">
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { resourceState } from "$lib/state/resources.svelte";
    import { specState } from "$lib/state/spec.svelte";
    import TextEditor from "./TextEditor.svelte";
    import AccordionGroup from "./AccordionGroup.svelte";
    import AccordionSection from "./AccordionSection.svelte";
    import { Input, NumberInput, Select, ColorInput, IconButton, GridSizePicker, GapInput, MarginInput } from "./forms";

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
    {#if workspaceState.currentWorkspaceId}
        <AccordionGroup storageKey="sidebar-accordion" defaultExpanded="project">
            {#snippet children({
                isExpanded,
                toggle,
            }: {
                isExpanded: (id: string) => boolean;
                toggle: (id: string) => void;
            })}
                <AccordionSection title="Project" expanded={isExpanded("project")} onclick={() => toggle("project")}>
                    {#snippet children()}
                        <div class="form-group">
                            <label for="project-name">Project Name</label>
                            <Input
                                id="project-name"
                                value={specState.current.projectName ?? "Untitled Project"}
                                oninput={(e) => {
                                    specState.current.projectName = e.currentTarget.value;
                                    markDirty();
                                }}
                            />
                        </div>

                        <div class="form-group">
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
                    {/snippet}
                </AccordionSection>

                <AccordionSection title="Page Layout" expanded={isExpanded("layout")} onclick={() => toggle("layout")}>
                    {#snippet children()}
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

                        <div class="form-group">
                            <GapInput
                                id="gap"
                                label="Gap"
                                value={specState.current.layout.gap}
                                oninput={(value) => {
                                    specState.current.layout.gap = value;
                                    markDirty();
                                }}
                            />
                        </div>

                        <div class="form-group">
                            <MarginInput
                                id="margin"
                                label="Margin"
                                value={specState.current.layout.margin}
                                oninput={(value) => {
                                    specState.current.layout.margin = value;
                                    markDirty();
                                }}
                            />
                        </div>
                    {/snippet}
                </AccordionSection>

                <AccordionSection
                    title="Output Settings"
                    expanded={isExpanded("output")}
                    onclick={() => toggle("output")}
                >
                    {#snippet children()}
                        <div class="form-group">
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
                    {/snippet}
                </AccordionSection>

                <AccordionSection title="Texts" expanded={isExpanded("texts")} onclick={() => toggle("texts")}>
                    {#snippet children()}
                        <TextEditor />
                    {/snippet}
                </AccordionSection>

                <AccordionSection title="Parameters" expanded={isExpanded("params")} onclick={() => toggle("params")}>
                    {#snippet children()}
                        {#if specState.current.params && specState.current.params.length > 0}
                            <ul class="params-list">
                                {#each specState.current.params as param}
                                    <li>
                                        <span class="param-name">{param.name}</span>
                                        <span class="param-type">{param.type}</span>
                                    </li>
                                {/each}
                            </ul>
                        {:else}
                            <p class="empty-message">No parameters defined</p>
                        {/if}
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

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
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

    .params-list {
        list-style: none;
        padding: 0;
        margin: 0;
        background: var(--bg-primary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    .params-list li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0.75rem;
        font-size: 0.85rem;
        border-bottom: 1px solid var(--border-subtle);
    }

    .params-list li:last-child {
        border-bottom: none;
    }

    .param-name {
        font-weight: 500;
        color: var(--text-primary);
    }

    .param-type {
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    .empty-message {
        color: var(--text-tertiary);
        font-style: italic;
        text-align: center;
        padding: 1rem;
        margin: 0;
        font-size: 0.85rem;
    }
</style>
