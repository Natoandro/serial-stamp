<script lang="ts">
	import { specState } from '$lib/state/spec.svelte';
	import { workspaceState } from '$lib/state/workspace.svelte';

	function markDirty() {
		workspaceState.isDirty = true;
	}

	function setGap(index: number, value: number) {
		const g = specState.current.layout.gap;
		let next: [number, number];
		if (typeof g === 'number') {
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
		if (typeof m === 'number') curr = [m, m, m, m];
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
</script>

<div class="panel">
	<h3>Layout</h3>
	<div class="grid-2">
		<div class="field-group">
			<label for="grid-size-x">Grid Size</label>
			<div class="row">
				<div class="sub-field">
					<span>X</span>
					<input
						id="grid-size-x"
						type="number"
						min="1"
						step="1"
						value={specState.current.layout['grid-size'][0]}
						oninput={(e) => {
							specState.current.layout['grid-size'][0] = Math.max(
								1,
								Math.trunc(Number(e.currentTarget.value))
							);
							markDirty();
						}}
					/>
				</div>
				<div class="sub-field">
					<span>Y</span>
					<input
						type="number"
						min="1"
						step="1"
						value={specState.current.layout['grid-size'][1]}
						oninput={(e) => {
							specState.current.layout['grid-size'][1] = Math.max(
								1,
								Math.trunc(Number(e.currentTarget.value))
							);
							markDirty();
						}}
					/>
				</div>
			</div>
		</div>

		<div class="field-group">
			<label for="gap-x">Gap</label>
			<div class="row">
				<div class="sub-field">
					<span>X</span>
					<input
						id="gap-x"
						type="number"
						step="0.5"
						value={typeof specState.current.layout.gap === 'number'
							? specState.current.layout.gap
							: specState.current.layout.gap[0]}
						oninput={(e) => setGap(0, Number(e.currentTarget.value))}
					/>
				</div>
				<div class="sub-field">
					<span>Y</span>
					<input
						type="number"
						step="0.5"
						value={typeof specState.current.layout.gap === 'number'
							? specState.current.layout.gap
							: specState.current.layout.gap[1]}
						oninput={(e) => setGap(1, Number(e.currentTarget.value))}
					/>
				</div>
			</div>
		</div>
	</div>

	<div class="field-group">
		<label for="margin-top">Margins</label>
		<div class="row margin-row">
			<div class="sub-field">
				<span>Top</span>
				<input
					id="margin-top"
					type="number"
					step="0.5"
					value={Array.isArray(specState.current.layout.margin) &&
					specState.current.layout.margin.length === 4
						? specState.current.layout.margin[0]
						: 0}
					oninput={(e) => setMargin4(0, Number(e.currentTarget.value))}
				/>
			</div>
			<div class="sub-field">
				<span>Right</span>
				<input
					type="number"
					step="0.5"
					value={Array.isArray(specState.current.layout.margin) &&
					specState.current.layout.margin.length === 4
						? specState.current.layout.margin[1]
						: 0}
					oninput={(e) => setMargin4(1, Number(e.currentTarget.value))}
				/>
			</div>
			<div class="sub-field">
				<span>Bottom</span>
				<input
					type="number"
					step="0.5"
					value={Array.isArray(specState.current.layout.margin) &&
					specState.current.layout.margin.length === 4
						? specState.current.layout.margin[2]
						: 0}
					oninput={(e) => setMargin4(2, Number(e.currentTarget.value))}
				/>
			</div>
			<div class="sub-field">
				<span>Left</span>
				<input
					type="number"
					step="0.5"
					value={Array.isArray(specState.current.layout.margin) &&
					specState.current.layout.margin.length === 4
						? specState.current.layout.margin[3]
						: 0}
					oninput={(e) => setMargin4(3, Number(e.currentTarget.value))}
				/>
			</div>
		</div>
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
	}

	h3 {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
		color: #111827;
	}

	.grid-2 {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.field-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		font-size: 0.85rem;
		font-weight: 500;
		color: #374151;
	}

	.row {
		display: flex;
		gap: 0.75rem;
	}

	.sub-field {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		flex: 1;
	}

	.sub-field span {
		font-size: 0.75rem;
		color: #6b7280;
	}

	input {
		width: 100%;
		padding: 0.4rem;
		border: 1px solid #d1d5db;
		border-radius: 6px;
		font-size: 0.9rem;
	}

	.margin-row {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
	}
</style>
