<script lang="ts">
	interface Props {
		onclick?: (e: MouseEvent & { currentTarget: HTMLButtonElement }) => void;
		type?: 'button' | 'submit' | 'reset';
		variant?: 'primary' | 'secondary' | 'danger';
		disabled?: boolean;
		class?: string;
		title?: string;
		ariaLabel?: string;
		children?: import('svelte').Snippet;
	}

	let {
		onclick,
		type = 'button',
		variant = 'secondary',
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
	class="button {variant} {className}"
	aria-label={ariaLabel}
>
	{#if children}
		{@render children()}
	{/if}
</button>

<style>
	.button {
		border: none;
		padding: 0.5rem 1rem;
		border-radius: var(--radius-md);
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: 500;
		transition: all var(--transition-fast);
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
	}

	.button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.button.primary {
		background: var(--button-primary-bg);
		color: var(--button-primary-text);
	}

	.button.primary:hover:not(:disabled) {
		background: var(--button-primary-bg-hover);
	}

	.button.secondary {
		background: var(--bg-secondary);
		color: var(--text-primary);
		border: 1px solid var(--border-normal);
	}

	.button.secondary:hover:not(:disabled) {
		background: var(--bg-hover);
		border-color: var(--border-strong);
	}

	.button.danger {
		background: var(--state-error);
		color: white;
	}

	.button.danger:hover:not(:disabled) {
		background: oklch(from var(--state-error) calc(l * 0.9) c h);
	}

	.button:focus-visible {
		outline: 2px solid var(--input-border-focus);
		outline-offset: 2px;
	}
</style>
