<script lang="ts">
    import { onMount } from "svelte";
    import { listen } from "@tauri-apps/api/event";
    import { invoke } from "@tauri-apps/api/core";
    import { open, save } from "@tauri-apps/plugin-dialog";
    import { workspaceState } from "$lib/state/workspace.svelte";
    import { specState } from "$lib/state/spec.svelte";

    interface WorkspaceInfo {
        workspaceId: string;
        workspaceDir: string;
    }

    onMount(() => {
        const unlistenPromise = listen<string>("menu://action", async (event) => {
            const action = event.payload;
            console.log("Menu action:", action);

            try {
                switch (action) {
                    case "project.new":
                        await handleNew();
                        break;
                    case "project.open":
                        await handleOpen();
                        break;
                    case "project.save":
                        await handleSave();
                        break;
                    case "project.save_as":
                        await handleSaveAs();
                        break;
                    case "export.pdf":
                        alert("Export PDF not implemented yet");
                        break;
                }
            } catch (e) {
                console.error("Menu action failed:", e);
                alert("Error: " + String(e));
            }
        });

        return () => {
            unlistenPromise.then((unlisten) => unlisten());
        };
    });

    async function handleNew() {
        const ws = await invoke<WorkspaceInfo>("workspace_new");
        workspaceState.currentWorkspaceId = ws.workspaceId;
        workspaceState.currentFilePath = null;
        workspaceState.isDirty = false;
    }

    async function handleOpen() {
        const selected = await open({
            multiple: false,
            filters: [{ name: "Stamp Project", extensions: ["stamp"] }],
        });

        if (selected && typeof selected === "string") {
            const ws = await invoke<WorkspaceInfo>("project_unpack", { filePath: selected });
            workspaceState.currentWorkspaceId = ws.workspaceId;
            workspaceState.currentFilePath = selected;
            workspaceState.isDirty = false;
        }
    }

    async function handleSave() {
        if (!workspaceState.currentWorkspaceId) return;

        // Save spec to workspace before packing
        await invoke("workspace_set_spec_json", {
            workspaceId: workspaceState.currentWorkspaceId,
            spec: specState.current,
        });

        if (workspaceState.currentFilePath) {
            await invoke("project_pack", {
                workspaceId: workspaceState.currentWorkspaceId,
                destPath: workspaceState.currentFilePath,
            });
            workspaceState.isDirty = false;
        } else {
            await handleSaveAs();
        }
    }

    async function handleSaveAs() {
        if (!workspaceState.currentWorkspaceId) return;

        const selected = await save({
            filters: [{ name: "Stamp Project", extensions: ["stamp"] }],
        });

        if (selected) {
            // Save spec to workspace before packing
            await invoke("workspace_set_spec_json", {
                workspaceId: workspaceState.currentWorkspaceId,
                spec: specState.current,
            });

            await invoke("project_pack", {
                workspaceId: workspaceState.currentWorkspaceId,
                destPath: selected,
            });
            workspaceState.currentFilePath = selected;
            workspaceState.isDirty = false;
        }
    }
</script>
