import { invoke } from '@tauri-apps/api/core';
import { open } from '@tauri-apps/plugin-dialog';

export class ResourceState {
	images = $state<string[]>([]);
	fonts = $state<string[]>([]);

	async refresh(workspaceId: string) {
		this.images = await invoke<string[]>('workspace_list_files', {
			workspaceId,
			category: 'images'
		});
		this.fonts = await invoke<string[]>('workspace_list_files', {
			workspaceId,
			category: 'fonts'
		});
	}

	async importImage(workspaceId: string) {
		const selected = await open({
			multiple: false,
			filters: [
				{
					name: 'Images',
					extensions: ['png', 'jpg', 'jpeg', 'webp', 'bmp', 'svg']
				}
			]
		});

		if (selected && typeof selected === 'string') {
			await invoke('workspace_add_file', {
				workspaceId,
				srcPath: selected,
				category: 'images'
			});
			await this.refresh(workspaceId);
		}
	}

	async importFont(workspaceId: string) {
		const selected = await open({
			multiple: false,
			filters: [{ name: 'Fonts', extensions: ['ttf', 'otf', 'woff', 'woff2'] }]
		});

		if (selected && typeof selected === 'string') {
			await invoke('workspace_add_file', {
				workspaceId,
				srcPath: selected,
				category: 'fonts'
			});
			await this.refresh(workspaceId);
		}
	}

	async remove(workspaceId: string, category: 'images' | 'fonts', filename: string) {
		await invoke('workspace_remove_file', {
			workspaceId,
			category,
			filename
		});
		await this.refresh(workspaceId);
	}

	reset() {
		this.images = [];
		this.fonts = [];
	}
}

export const resourceState = new ResourceState();
