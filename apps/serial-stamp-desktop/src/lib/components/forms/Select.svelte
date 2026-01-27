<script lang="ts">
	interface Props {
		value: string;
		onchange?: (e: Event & { currentTarget: HTMLSelectElement }) => void;
		id?: string;
		disabled?: boolean;
		class?: string;
		ariaLabel?: string;
		children?: import('svelte').Snippet;
	}

	let {
		value = $bindable(''),
		onchange,
		id,
		disabled = false,
		class: className = '',
		ariaLabel,
		children,
	}: Props = $props();
</script>

<select
	{id}
	{value}
	{disabled}
	{onchange}
	class="select {className}"
	aria-label={ariaLabel}
>
	{#if children}
		{@render children()}
	{/if}
</select>

<style>
	.select {
		padding: 0.4rem;
		border: 1px solid var(--input-border);
		border-radius: var(--radius-md);
		font-size: 0.9rem;
		background: var(--input-bg);
		color: var(--input-text);
		width: 100%;
		box-sizing: border-box;
		transition: border-color var(--transition-fast);
		cursor: pointer;
	}

	.select:hover:not(:disabled) {
		border-color: var(--input-border-hover);
	}

	.select:focus {
		outline: none;
		border-color: var(--input-border-focus);
		box-shadow: 0 0 0 3px var(--bg-accent-subtle);
	}

	.select:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}
</style>
