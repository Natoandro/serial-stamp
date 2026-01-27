<script lang="ts">
	interface Props {
		class?: string;
		size?: number;
	}

	let { class: className = '', size = 16 }: Props = $props();
</script>

<svg
	class={className}
	xmlns="http://www.w3.org/2000/svg"
	width={size}
	height={size}
	viewBox="0 0 16 16"
	fill="none"
	stroke="currentColor"
	stroke-width="1.5"
	stroke-linecap="round"
	stroke-linejoin="round"
>
	<rect x="2" y="2" width="5" height="5" />
	<rect x="9" y="2" width="5" height="5" />
	<rect x="2" y="9" width="5" height="5" />
	<rect x="9" y="9" width="5" height="5" />
</svg>
