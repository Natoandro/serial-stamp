<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";

    type WorkspaceInfo = {
        workspaceId: string;
        workspaceDir: string;
    };

    let creating = false;
    let saving = false;

    let workspace: WorkspaceInfo | null = null;

    let specToml = "";
    let dirty = false;

    let error: string | null = null;

    async function newWorkspace() {
        creating = true;
        error = null;
        workspace = null;
        specToml = "";
        dirty = false;

        try {
            workspace = await invoke<WorkspaceInfo>("workspace_new");
            specToml = await invoke<string>("workspace_get_spec", {
                workspaceId: workspace.workspaceId,
            });
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
            specToml = await invoke<string>("workspace_get_spec", {
                workspaceId: workspace.workspaceId,
            });
            dirty = false;
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        }
    }

    function onSpecInput(e: Event) {
        const v = (e.target as HTMLTextAreaElement).value;
        specToml = v;
        dirty = true;
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
            <h2>Spec (<code>spec.toml</code>)</h2>

            <div class="editorActions">
                <button on:click={saveSpec} disabled={!workspace || !dirty || saving}>
                    {saving ? "Saving…" : "Save spec.toml"}
                </button>
                <button on:click={reloadSpec} disabled={!workspace || saving}> Reload from disk </button>
                {#if dirty}
                    <span class="badge">unsaved changes</span>
                {/if}
            </div>

            <textarea
                class="editor monospace"
                rows="24"
                value={specToml}
                on:input={onSpecInput}
                placeholder="Click “New Project” to load a default spec.toml…"
                disabled={!workspace}
            ></textarea>

            <p class="hint">
                Step 1: workspace lifecycle + spec read/write. Next steps add assets, packing <code>.stamp</code>, and
                preview/PDF.
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

    .editor {
        width: 100%;
        resize: vertical;
        padding: 0.75rem;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        background: #f9fafb;
        line-height: 1.35;
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
    }
</style>
