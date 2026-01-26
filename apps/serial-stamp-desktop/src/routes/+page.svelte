<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { specState, type StampSpec } from "$lib/state/spec.svelte";
    import { resourceState } from "$lib/state/resources.svelte";

    import AppLayout from "$lib/components/AppLayout.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import LayoutEditor from "$lib/components/LayoutEditor.svelte";
    import TextEditor from "$lib/components/TextEditor.svelte";
    import PreviewPanel from "$lib/components/PreviewPanel.svelte";

    let creating = false;
    let error: string | null = null;

    async function newWorkspace() {
        creating = true;
        error = null;
        specState.reset();
        resourceState.reset();

        try {
            const ws = await invoke<{ workspaceId: string; workspaceDir: string }>("workspace_new");

            workspaceState.currentWorkspaceId = ws.workspaceId;
            workspaceState.currentFilePath = null;
            workspaceState.isDirty = false;

            const loadedSpec = await invoke<StampSpec>("workspace_get_spec_json", {
                workspaceId: ws.workspaceId,
            });
            specState.set(loadedSpec);

            // Even a new workspace might have default files eventually, so good practice to refresh
            await resourceState.refresh(ws.workspaceId);
        } catch (e) {
            error = e instanceof Error ? e.message : String(e);
        } finally {
            creating = false;
        }
    }
</script>

<AppLayout>
    {#snippet sidebar()}
        <Sidebar {newWorkspace} />
    {/snippet}

    {#if workspaceState.currentWorkspaceId}
        <PreviewPanel />
        <LayoutEditor />
        <TextEditor />
    {:else}
        <div class="welcome-screen">
            <div class="content">
                <h1>SerialStamp Desktop</h1>
                <p>Create a new project or open an existing one to get started.</p>
                <button class="primary" onclick={newWorkspace} disabled={creating}>
                    {creating ? "Creating..." : "Create New Project"}
                </button>
            </div>
        </div>
    {/if}

    {#if error}
        <div class="error-toast">
            <strong>Error:</strong>
            {error}
            <button onclick={() => (error = null)}>×</button>
        </div>
    {/if}
</AppLayout>

<style>
    .welcome-screen {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #4b5563;
    }

    .content {
        text-align: center;
        max-width: 400px;
    }

    h1 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        color: #111827;
    }

    p {
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    button.primary {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        font-size: 1rem;
        cursor: pointer;
        transition: background 0.2s;
    }

    button.primary:hover {
        background: #1d4ed8;
    }

    button.primary:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .error-toast {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        background: #fee2e2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        max-width: 400px;
        z-index: 100;
    }

    .error-toast button {
        background: none;
        border: none;
        font-size: 1.25rem;
        cursor: pointer;
        color: #991b1b;
        padding: 0;
        line-height: 1;
    }
</style>
