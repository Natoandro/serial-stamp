export class WorkspaceState {
	currentWorkspaceId = $state<string | null>(null);
	currentFilePath = $state<string | null>(null);
	isDirty = $state(false);

	reset() {
		this.currentWorkspaceId = null;
		this.currentFilePath = null;
		this.isDirty = false;
	}
}

export const workspaceState = new WorkspaceState();
