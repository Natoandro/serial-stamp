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

<style>
    :global(body) {
        margin: 0;
        padding: 0;
        font-family:
            system-ui,
            -apple-system,
            sans-serif;
        box-sizing: border-box;
        overflow: hidden;
    }

    :global(*),
    :global(*::before),
    :global(*::after) {
        box-sizing: inherit;
    }
</style>
