<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";
    import { defaultSpec, parseSpecToml, serializeSpecToToml, type Spec, type TextSpec } from "$lib/spec/spec";

    type WorkspaceInfo = {
        workspaceId: string;
        workspaceDir: string;
    };

    let creating = false;
    let saving = false;

    let workspace: WorkspaceInfo | null = null;

    let spec: Spec = defaultSpec();
    let dirty = false;

    let error: string | null = null;

    async function newWorkspace() {
        creating = true;
        error = null;
        workspace = null;
        spec = defaultSpec();
        dirty = false;

        try {
            workspace = await invoke<WorkspaceInfo>("workspace_new");
            const tomlText = await invoke<string>("workspace_get_spec", {
                workspaceId: workspace.workspaceId,
            });
            spec = parseSpecToml(tomlText);
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        } finally {
            creating = false;
        }
    }

    async function saveSpec() {
        if (!workspace) return;

        saving = true;
        error = null;

        try {
            const specToml = serializeSpecToToml(spec);
            await invoke("workspace_set_spec", {
                workspaceId: workspace.workspaceId,
                specToml,
            });
            dirty = false;
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        } finally {
            saving = false;
        }
    }

    async function reloadSpec() {
        if (!workspace) return;

        error = null;
        try {
            const tomlText = await invoke<string>("workspace_get_spec", {
                workspaceId: workspace.workspaceId,
            });
            spec = parseSpecToml(tomlText);
            dirty = false;
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        }
    }

    function markDirty() {
        dirty = true;
    }

    function setNumTuple2(
        path: "layout.gridSize" | "texts.position",
        index: number,
        value: number,
        textIndex?: number,
    ) {
        if (path === "layout.gridSize") {
            const curr = spec.layout.gridSize;
            spec.layout.gridSize = index === 0 ? [value, curr[1]] : [curr[0], value];
            markDirty();
            return;
        }
        if (path === "texts.position" && typeof textIndex === "number") {
            const t = spec.texts[textIndex];
            if (!t) return;
            const curr = t.position;
            t.position = index === 0 ? [value, curr[1]] : [curr[0], value];
            markDirty();
        }
    }

    function setGap(index: number, value: number) {
        const g = spec.layout.gap;

        // If gap is a single number, keep it as a single number when both axes are meant to match.
        // Since the UI edits x/y independently, switching to a tuple on first edit is fine.
        if (typeof g === "number") {
            spec.layout.gap = index === 0 ? [value, g] : [g, value];
        } else {
            const curr = g;
            spec.layout.gap = index === 0 ? [value, curr[1]] : [curr[0], value];
        }

        markDirty();
    }

    function setMargin4(index: number, value: number) {
        const m = spec.layout.margin;
        let curr: [number, number, number, number];
        if (typeof m === "number") curr = [m, m, m, m];
        else if (Array.isArray(m) && m.length === 2) curr = [m[0], m[1], m[0], m[1]];
        else if (Array.isArray(m) && m.length === 4) curr = [m[0], m[1], m[2], m[3]];
        else curr = [0, 0, 0, 0];

        const next: [number, number, number, number] =
            index === 0
                ? [value, curr[1], curr[2], curr[3]]
                : index === 1
                  ? [curr[0], value, curr[2], curr[3]]
                  : index === 2
                    ? [curr[0], curr[1], value, curr[3]]
                    : [curr[0], curr[1], curr[2], value];

        spec.layout.margin = next;
        markDirty();
    }

    function addText() {
        const t: TextSpec = {
            template: "",
            position: [0, 0],
            ttf: null,
            size: 16,
            color: "black",
        };
        spec.texts = [...spec.texts, t];
        markDirty();
    }

    function removeText(i: number) {
        spec.texts = spec.texts.filter((_, idx) => idx !== i);
        markDirty();
    }

    function updateText(i: number, patch: Partial<TextSpec>) {
        const next = spec.texts.map((t, idx) => (idx === i ? { ...t, ...patch } : t));
        spec.texts = next;
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

            {#if workspace}
                <div class="kv">
                    <div class="k">workspaceId</div>
                    <div class="v monospace">{workspace.workspaceId}</div>

                    <div class="k">workspaceDir</div>
                    <div class="v monospace">{workspace.workspaceDir}</div>
                </div>

                <p class="hint">
                    Workspace lives in a temporary directory. The spec is stored as <code>spec.toml</code>.
                </p>
            {:else}
                <p class="hint">Create a new project to start editing <code>spec.toml</code>.</p>
            {/if}
        </section>

        <section class="panel">
            <h2>Spec Builder</h2>

            <div class="editorActions">
                <button on:click={saveSpec} disabled={!workspace || !dirty || saving}>
                    {saving ? "Saving…" : "Save"}
                </button>
                <button on:click={reloadSpec} disabled={!workspace || saving}> Reload </button>
                {#if dirty}
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
                            value={spec.stackSize}
                            on:input={(e) => {
                                spec.stackSize = Math.max(1, Math.trunc(Number((e.target as HTMLInputElement).value)));
                                markDirty();
                            }}
                            disabled={!workspace}
                        />
                    </label>

                    <label class="field">
                        <span class="label">source-image</span>
                        <input
                            type="text"
                            value={spec.sourceImage}
                            on:input={(e) => {
                                spec.sourceImage = (e.target as HTMLInputElement).value;
                                markDirty();
                            }}
                            placeholder="assets/..."
                            disabled={!workspace}
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
                            value={spec.layout.gridSize[0]}
                            on:input={(e) =>
                                setNumTuple2(
                                    "layout.gridSize",
                                    0,
                                    Math.max(1, Math.trunc(Number((e.target as HTMLInputElement).value))),
                                )}
                            disabled={!workspace}
                        />
                    </label>
                    <label class="field">
                        <span class="label">grid-size (y)</span>
                        <input
                            type="number"
                            min="1"
                            step="1"
                            value={spec.layout.gridSize[1]}
                            on:input={(e) =>
                                setNumTuple2(
                                    "layout.gridSize",
                                    1,
                                    Math.max(1, Math.trunc(Number((e.target as HTMLInputElement).value))),
                                )}
                            disabled={!workspace}
                        />
                    </label>
                </div>

                <div class="row">
                    <label class="field">
                        <span class="label">gap (x)</span>
                        <input
                            type="number"
                            step="0.5"
                            value={typeof spec.layout.gap === "number" ? spec.layout.gap : spec.layout.gap[0]}
                            on:input={(e) => setGap(0, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspace}
                        />
                    </label>
                    <label class="field">
                        <span class="label">gap (y)</span>
                        <input
                            type="number"
                            step="0.5"
                            value={typeof spec.layout.gap === "number" ? spec.layout.gap : spec.layout.gap[1]}
                            on:input={(e) => setGap(1, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspace}
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
                            value={Array.isArray(spec.layout.margin) && spec.layout.margin.length === 4
                                ? spec.layout.margin[0]
                                : 0}
                            on:input={(e) => setMargin4(0, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspace}
                        />
                    </label>
                    <label class="field">
                        <span class="label">right</span>
                        <input
                            type="number"
                            step="0.5"
                            value={Array.isArray(spec.layout.margin) && spec.layout.margin.length === 4
                                ? spec.layout.margin[1]
                                : 0}
                            on:input={(e) => setMargin4(1, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspace}
                        />
                    </label>
                    <label class="field">
                        <span class="label">bottom</span>
                        <input
                            type="number"
                            step="0.5"
                            value={Array.isArray(spec.layout.margin) && spec.layout.margin.length === 4
                                ? spec.layout.margin[2]
                                : 0}
                            on:input={(e) => setMargin4(2, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspace}
                        />
                    </label>
                    <label class="field">
                        <span class="label">left</span>
                        <input
                            type="number"
                            step="0.5"
                            value={Array.isArray(spec.layout.margin) && spec.layout.margin.length === 4
                                ? spec.layout.margin[3]
                                : 0}
                            on:input={(e) => setMargin4(3, Number((e.target as HTMLInputElement).value))}
                            disabled={!workspace}
                        />
                    </label>
                </div>

                <h3>texts</h3>
                <div class="editorActions">
                    <button on:click={addText} disabled={!workspace}>Add text</button>
                </div>

                {#if spec.texts.length === 0}
                    <p class="hint">No texts. Add one to begin.</p>
                {:else}
                    <div class="texts">
                        {#each spec.texts as t, i (i)}
                            <div class="textCard">
                                <div class="textHeader">
                                    <strong>Text #{i + 1}</strong>
                                    <button on:click={() => removeText(i)} disabled={!workspace}>Remove</button>
                                </div>

                                <div class="row">
                                    <label class="field">
                                        <span class="label">template</span>
                                        <input
                                            type="text"
                                            value={t.template}
                                            on:input={(e) =>
                                                updateText(i, { template: (e.target as HTMLInputElement).value })}
                                            disabled={!workspace}
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
                                            disabled={!workspace}
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
                                            disabled={!workspace}
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
                                                updateText(i, { ttf: v === "" ? null : v });
                                            }}
                                            disabled={!workspace}
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
                                            disabled={!workspace}
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
                                            disabled={!workspace}
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
        grid-template-columns: 9rem 1fr;
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
