<script lang="ts">
	interface Props {
		onclick?: (e: MouseEvent & { currentTarget: HTMLButtonElement }) => void;
		type?: 'button' | 'submit' | 'reset';
		variant?: 'default' | 'danger';
		disabled?: boolean;
		class?: string;
		title?: string;
		ariaLabel?: string;
		children?: import('svelte').Snippet;
	}

	let {
		onclick,
		type = 'button',
		variant = 'default',
		disabled = false,
		class: className = '',
		title,
		ariaLabel,
		children,
	}: Props = $props();
</script>

<button
	{type}
	{disabled}
	{onclick}
	{title}
	class="icon-btn {variant} {className}"
	aria-label={ariaLabel}
>
	{#if children}
		{@render children()}
	{/if}
</button>

<style>
	.icon-btn {
		padding: 0;
		width: 20px;
		height: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		background: none;
		cursor: pointer;
		font-weight: bold;
		color: var(--icon-primary);
		border-radius: var(--radius-sm);
		transition: all var(--transition-fast);
	}

	.icon-btn:hover:not(:disabled) {
		background: var(--bg-hover);
		color: var(--icon-hover);
	}

	.icon-btn.danger:hover:not(:disabled) {
		color: var(--state-error);
		background: oklch(from var(--state-error) l c h / 0.1);
	}

	.icon-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.icon-btn:focus-visible {
		outline: 2px solid var(--input-border-focus);
		outline-offset: 2px;
	}
</style>
