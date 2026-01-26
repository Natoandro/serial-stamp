<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { specState, defaultSpec, type TextSpec, type StampSpec } from "$lib/state/spec.svelte";

    let creating = false;
    let saving = false;
    let error: string | null = null;

    async function newWorkspace() {
        creating = true;
        error = null;
        // Reset spec to default locally first
        specState.reset();

        try {
            const ws = await invoke<{ workspaceId: string; workspaceDir: string }>("workspace_new");

            workspaceState.currentWorkspaceId = ws.workspaceId;
            workspaceState.currentFilePath = null;
            workspaceState.isDirty = false;

            const loadedSpec = await invoke<StampSpec>("workspace_get_spec_json", {
                workspaceId: ws.workspaceId,
            });
            specState.set(loadedSpec);
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        } finally {
            creating = false;
        }
    }

    async function saveSpec() {
        if (!workspaceState.currentWorkspaceId) return;

        saving = true;
        error = null;

        try {
            await invoke("workspace_set_spec_json", {
                workspaceId: workspaceState.currentWorkspaceId,
                spec: specState.current,
            });
            workspaceState.isDirty = false;
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        } finally {
            saving = false;
        }
    }

    async function reloadSpec() {
        if (!workspaceState.currentWorkspaceId) return;

        error = null;
        try {
            const loadedSpec = await invoke<StampSpec>("workspace_get_spec_json", {
                workspaceId: workspaceState.currentWorkspaceId,
            });
            specState.set(loadedSpec);
            workspaceState.isDirty = false;
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        }
    }

    function markDirty() {
        workspaceState.isDirty = true;
    }

    function setNumTuple2(
        path: "layout.gridSize" | "texts.position",
        index: number,
        value: number,
        textIndex?: number,
    ) {
        if (path === "layout.gridSize") {
            const curr = specState.current.layout["grid-size"];
            if (index === 0) specState.current.layout["grid-size"] = [value, curr[1]];
            else specState.current.layout["grid-size"] = [curr[0], value];
        }
        if (path === "texts.position" && typeof textIndex === "number") {
            const t = specState.current.texts[textIndex];
            if (t) {
                const curr = t.position;
                if (index === 0) t.position = [value, curr[1]];
                else t.position = [curr[0], value];
            }
        }
        markDirty();
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

    function addText() {
        const t: TextSpec = {
            template: "",
            position: [0, 0],
            size: 16,
            color: "black",
        };
        specState.current.texts.push(t);
        markDirty();
    }

    function removeText(i: number) {
        specState.current.texts.splice(i, 1);
        markDirty();
    }

    function updateText(i: number, patch: Partial<TextSpec>) {
        const t = specState.current.texts[i];
        if (t) {
            Object.assign(t, patch);
        }
        markDirty();
    }
</script>

<div class="page">
    <header class="header">
        <h1>SerialStamp Desktop</h1>
        <div class="headerActions">
            <button class="primary" on:click={newWorkspace} disabled={creating}>
                {creating ? "Creating…" : "New Project (temp workspace)"}
            </button>
        </div>
    </header>

    <main class="grid">
        <section class="panel">
            <h2>Project</h2>

            {#if workspaceState.currentWorkspaceId}
                <div class="kv">
                    <div class="k">ID</div>
                    <div class="v monospace">{workspaceState.currentWorkspaceId}</div>

                    <div class="k">File</div>
                    <div class="v monospace">
                        {workspaceState.currentFilePath ?? "(unsaved new project)"}
                    </div>
                </div>

                <p class="hint">
                    Workspace lives in a temporary directory. The spec is stored as <code>spec.toml</code>.
                </p>
            {:else}
                <p class="hint">Create or open a project to start editing.</p>
            {/if}
        </section>

        <section class="panel">
            <h2>Spec Builder</h2>

            <div class="editorActions">
                <button
                    on:click={saveSpec}
                    disabled={!workspaceState.currentWorkspaceId || !workspaceState.isDirty || saving}
                >
                    {saving ? "Saving…" : "Save"}
                </button>
                <button on:click={reloadSpec} disabled={!workspaceState.currentWorkspaceId || saving}> Reload </button>
                {#if workspaceState.isDirty}
                    <span class="badge">unsaved changes</span>
                {/if}
            </div>

            <div class="form">
                <div class="row">
                    <label class="field">
                        <span class="label">stack-size</span>
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={specState.current["stack-size"]}
                            on:input={(e) => {
                                specState.current["stack-size"] = Math.max(
                                    1,
                                    Math.trunc(Number((e.target as HTMLInputElement).value)),
                                );
                                markDirty();
                            }}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>

                    <label class="field">
                        <span class="label">source-image</span>
                        <input
                            type="text"
                            value={specState.current["source-image"]}
                            on:input={(e) => {
                                specState.current["source-image"] = (e.target as HTMLInputElement).value;
                                markDirty();
                            }}
                            placeholder="assets/..."
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                </div>

                <h3>layout</h3>
                <div class="row">
                    <label class="field">
                        <span class="label">grid-size (x)</span>
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={specState.current.layout["grid-size"][0]}
                            on:input={(e) =>
                                setNumTuple2(
                                    "layout.gridSize",
                                    0,
                                    Math.max(1, Math.trunc(Number((e.target as HTMLInputElement).value))),
                                )}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                    <label class="field">
                        <span class="label">grid-size (y)</span>
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={specState.current.layout["grid-size"][1]}
                            on:input={(e) =>
                                setNumTuple2(
                                    "layout.gridSize",
                                    1,
                                    Math.max(1, Math.trunc(Number((e.target as HTMLInputElement).value))),
                                )}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                </div>

                <div class="row">
                    <label class="field">
                        <span class="label">gap (x)</span>
                        <input
                            type="number"
                            step="0.5"
                            value={typeof specState.current.layout.gap === "number"
                                ? specState.current.layout.gap
                                : specState.current.layout.gap[0]}
                            on:input={(e) => setGap(0, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                    <label class="field">
                        <span class="label">gap (y)</span>
                        <input
                            type="number"
                            step="0.5"
                            value={typeof specState.current.layout.gap === "number"
                                ? specState.current.layout.gap
                                : specState.current.layout.gap[1]}
                            on:input={(e) => setGap(1, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                </div>

                <h4>margin (top/right/bottom/left)</h4>
                <div class="row">
                    <label class="field">
                        <span class="label">top</span>
                        <input
                            type="number"
                            step="0.5"
                            value={Array.isArray(specState.current.layout.margin) &&
                            specState.current.layout.margin.length === 4
                                ? specState.current.layout.margin[0]
                                : 0}
                            on:input={(e) => setMargin4(0, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                    <label class="field">
                        <span class="label">right</span>
                        <input
                            type="number"
                            step="0.5"
                            value={Array.isArray(specState.current.layout.margin) &&
                            specState.current.layout.margin.length === 4
                                ? specState.current.layout.margin[1]
                                : 0}
                            on:input={(e) => setMargin4(1, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                    <label class="field">
                        <span class="label">bottom</span>
                        <input
                            type="number"
                            step="0.5"
                            value={Array.isArray(specState.current.layout.margin) &&
                            specState.current.layout.margin.length === 4
                                ? specState.current.layout.margin[2]
                                : 0}
                            on:input={(e) => setMargin4(2, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                    <label class="field">
                        <span class="label">left</span>
                        <input
                            type="number"
                            step="0.5"
                            value={Array.isArray(specState.current.layout.margin) &&
                            specState.current.layout.margin.length === 4
                                ? specState.current.layout.margin[3]
                                : 0}
                            on:input={(e) => setMargin4(3, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspaceState.currentWorkspaceId}
                        />
                    </label>
                </div>

                <h3>texts</h3>
                <div class="editorActions">
                    <button on:click={addText} disabled={!workspaceState.currentWorkspaceId}>Add text</button>
                </div>

                {#if specState.current.texts.length === 0}
                    <p class="hint">No texts. Add one to begin.</p>
                {:else}
                    <div class="texts">
                        {#each specState.current.texts as t, i (i)}
                            <div class="textCard">
                                <div class="textHeader">
                                    <strong>Text #{i + 1}</strong>
                                    <button on:click={() => removeText(i)} disabled={!workspaceState.currentWorkspaceId}
                                        >Remove</button
                                    >
                                </div>

                                <div class="row">
                                    <label class="field">
                                        <span class="label">template</span>
                                        <input
                                            type="text"
                                            value={t.template}
                                            on:input={(e) =>
                                                updateText(i, { template: (e.target as HTMLInputElement).value })}
                                            disabled={!workspaceState.currentWorkspaceId}
                                        />
                                    </label>
                                </div>

                                <div class="row">
                                    <label class="field">
                                        <span class="label">position x</span>
                                        <input
                                            type="number"
                                            step="0.5"
                                            value={t.position[0]}
                                            on:input={(e) =>
                                                setNumTuple2(
                                                    "texts.position",
                                                    0,
                                                    Number((e.target as HTMLInputElement).value),
                                                    i,
                                                )}
                                            disabled={!workspaceState.currentWorkspaceId}
                                        />
                                    </label>
                                    <label class="field">
                                        <span class="label">position y</span>
                                        <input
                                            type="number"
                                            step="0.5"
                                            value={t.position[1]}
                                            on:input={(e) =>
                                                setNumTuple2(
                                                    "texts.position",
                                                    1,
                                                    Number((e.target as HTMLInputElement).value),
                                                    i,
                                                )}
                                            disabled={!workspaceState.currentWorkspaceId}
                                        />
                                    </label>
                                </div>

                                <div class="row">
                                    <label class="field">
                                        <span class="label">ttf (optional)</span>
                                        <input
                                            type="text"
                                            value={t.ttf ?? ""}
                                            placeholder="assets/font.ttf"
                                            on:input={(e) => {
                                                const v = (e.target as HTMLInputElement).value.trim();
                                                updateText(i, { ttf: v === "" ? undefined : v });
                                            }}
                                            disabled={!workspaceState.currentWorkspaceId}
                                        />
                                    </label>

                                    <label class="field">
                                        <span class="label">size</span>
                                        <input
                                            type="number"
                                            min="1"
                                            step="1"
                                            value={t.size}
                                            on:input={(e) =>
                                                updateText(i, {
                                                    size: Math.max(
                                                        1,
                                                        Math.trunc(Number((e.target as HTMLInputElement).value)),
                                                    ),
                                                })}
                                            disabled={!workspaceState.currentWorkspaceId}
                                        />
                                    </label>

                                    <label class="field">
                                        <span class="label">color</span>
                                        <input
                                            type="text"
                                            value={typeof t.color === "string" ? t.color : JSON.stringify(t.color)}
                                            placeholder="black / #ff00aa"
                                            on:input={(e) =>
                                                updateText(i, { color: (e.target as HTMLInputElement).value })}
                                            disabled={!workspaceState.currentWorkspaceId}
                                        />
                                    </label>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>

            <p class="hint">
                This UI edits structured fields and saves to <code>spec.toml</code> for Python compatibility.
            </p>
        </section>
    </main>

    {#if error}
        <section class="panel errorPanel">
            <h2>Error</h2>
            <pre class="monospace">{error}</pre>
        </section>
    {/if}
</div>

<style>
    .page {
        padding: 1rem;
        display: grid;
        gap: 1rem;
        max-width: 1100px;
        margin: 0 auto;
    }

    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .headerActions {
        display: flex;
        gap: 0.5rem;
    }

    .grid {
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 1rem;
        align-items: start;
    }

    .panel {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1rem;
        background: white;
    }

    .hint {
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: 0.75rem;
    }

    .kv {
        display: grid;
        grid-template-columns: 4rem 1fr;
        gap: 0.25rem 0.75rem;
        align-items: baseline;
        margin-top: 0.5rem;
    }

    .k {
        color: #6b7280;
        font-size: 0.9rem;
    }

    .v {
        overflow-wrap: anywhere;
    }

    .editorActions {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0 0.75rem 0;
        flex-wrap: wrap;
    }

    .badge {
        display: inline-block;
        font-size: 0.8rem;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a3412;
    }

    .form {
        display: grid;
        gap: 1rem;
    }

    .row {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.75rem;
        align-items: end;
    }

    .field {
        display: grid;
        gap: 0.35rem;
    }

    .label {
        font-size: 0.85rem;
        color: #6b7280;
    }

    input[type="text"],
    input[type="number"] {
        padding: 0.55rem 0.65rem;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        background: #f9fafb;
    }

    h3 {
        margin: 0.25rem 0 0 0;
    }

    h4 {
        margin: 0.25rem 0 0 0;
        color: #374151;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .texts {
        display: grid;
        gap: 0.75rem;
    }

    .textCard {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 0.75rem;
        background: #fff;
    }

    .textHeader {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
    }

    button {
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        background: white;
        cursor: pointer;
    }

    button.primary {
        border-color: #2563eb;
        background: #2563eb;
        color: white;
    }

    button[disabled] {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .monospace {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    }

    pre {
        padding: 0.75rem;
        background: #0b1220;
        color: #e5e7eb;
        border-radius: 10px;
        overflow: auto;
    }

    .errorPanel {
        border-color: #fecaca;
        background: #fff1f2;
    }

    @media (max-width: 900px) {
        .grid {
            grid-template-columns: 1fr;
        }

        .row {
            grid-template-columns: 1fr;
        }
    }
</style>
