<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { specState, type StampSpec } from "$lib/state/spec.svelte";
    import { resourceState } from "$lib/state/resources.svelte";

    import AppLayout from "$lib/components/AppLayout.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
    import PreviewPanel from "$lib/components/PreviewPanel.svelte";
    import { Button } from "$lib/components/forms";

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

{#snippet sidebarContent()}
    <Sidebar />
{/snippet}

<AppLayout sidebar={sidebarContent}>
    {#if workspaceState.currentWorkspaceId}
        <div class="workspace-layout">
            <PreviewPanel />
        </div>
    {:else}
        <div class="welcome-screen">
            <div class="content">
                <h1>SerialStamp Desktop</h1>
                <p>Create a new project or open an existing one to get started.</p>
                <Button variant="primary" onclick={newWorkspace} disabled={creating}>
                    {creating ? "Creating..." : "Create New Project"}
                </Button>
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
    .workspace-layout {
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        background: #f3f4f6;
        overflow-y: auto;
        padding: 1rem;
    }

    .welcome-screen {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #4b5563;
        background: #f9fafb;
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

    :global(.welcome-screen .button.primary) {
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
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
