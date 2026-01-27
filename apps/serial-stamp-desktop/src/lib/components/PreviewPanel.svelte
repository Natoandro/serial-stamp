<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { specState } from "$lib/state/spec.svelte";

    let previewSrc: string | null = $state(null);
    let loading = $state(false);
    let error: string | null = $state(null);

    async function generatePreview() {
        if (!workspaceState.currentWorkspaceId) return;

        loading = true;
        error = null;

        try {
            // Ensure spec is saved before generating
            // The Rust command `preview_generate` reads from the workspace files on disk
            // so we must save the current in-memory spec to disk first.
            await invoke("workspace_set_spec_json", {
                workspaceId: workspaceState.currentWorkspaceId,
                spec: specState.current,
            });

            const b64 = await invoke<string>("preview_generate", {
                workspaceId: workspaceState.currentWorkspaceId,
            });
            previewSrc = `data:image/png;base64,${b64}`;
        } catch (e) {
            console.error(e);
            error = String(e);
        } finally {
            loading = false;
        }
    }
</script>

<div class="panel">
    <div class="header">
        <h3>Preview</h3>
        <button onclick={generatePreview} disabled={loading} class="secondary-sm">
            {loading ? "Generating..." : "Refresh Preview"}
        </button>
    </div>

    <div class="preview-area">
        {#if loading}
            <div class="placeholder">
                <div class="spinner"></div>
                <p>Generating preview...</p>
            </div>
        {:else if error}
            <div class="placeholder error">
                <p>Preview failed</p>
                <code class="error-msg">{error}</code>
            </div>
        {:else if previewSrc}
            <div class="image-wrapper">
                <img src={previewSrc} alt="Stamp Preview" />
            </div>
        {:else}
            <div class="placeholder">
                <p>Click refresh to generate a preview.</p>
            </div>
        {/if}
    </div>
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
        width: 100%;
        height: 100%;
        box-sizing: border-box;
    }

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
    }

    h3 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
    }

    button.secondary-sm {
        background: white;
        color: #374151;
        border: 1px solid #d1d5db;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-size: 0.85rem;
        cursor: pointer;
        font-weight: 500;
    }

    button.secondary-sm:hover {
        background: #f3f4f6;
        border-color: #9ca3af;
    }

    button.secondary-sm:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .preview-area {
        flex-grow: 1;
        min-height: 0; /* Allow shrinking if needed */
        width: 100%;
        background: #f9fafb;
        border: 1px dashed #d1d5db;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
    }

    .image-wrapper {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        box-sizing: border-box;
        overflow: auto;
    }

    img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }

    .placeholder {
        text-align: center;
        color: #6b7280;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .placeholder p {
        margin: 0;
        font-size: 0.9rem;
    }

    .error {
        color: #b91c1c;
    }

    .error-msg {
        font-size: 0.8rem;
        background: #fee2e2;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        max-width: 100%;
        overflow-wrap: anywhere;
    }

    .spinner {
        width: 24px;
        height: 24px;
        border: 3px solid #e5e7eb;
        border-top-color: #3b82f6;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>
