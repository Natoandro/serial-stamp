<script lang="ts">
    import favicon from "$lib/assets/favicon.svg";
    import MenuController from "$lib/MenuController.svelte";

    let { children } = $props();
</script>

<svelte:head>
    <link rel="icon" href={favicon} />
</svelte:head>

<MenuController />
{@render children()}
