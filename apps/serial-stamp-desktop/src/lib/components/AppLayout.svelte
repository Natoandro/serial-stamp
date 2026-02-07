<script lang="ts">
    import type { Snippet } from "svelte";

    let {
        sidebar,
        children,
        showSidebar = true,
    } = $props<{
        sidebar: Snippet;
        children: Snippet;
        showSidebar?: boolean;
    }>();
</script>

<div class="app-layout">
    {#if showSidebar}
        <div class="sidebar-wrapper">
            {@render sidebar()}
        </div>
    {/if}
    <main class="main-content">
        {@render children()}
    </main>
</div>

<style>
    .app-layout {
        display: flex;
        width: 100%;
        height: 100vh;
        overflow: hidden;
        background: #fff;
    }

    .sidebar-wrapper {
        flex-shrink: 0;
        height: 100%;
        z-index: 10;
        display: flex;
        border-right: 1px solid #e5e7eb;
    }

    .main-content {
        flex: 1; /* Robustly fill remaining space */
        height: 100%;
        min-width: 0; /* Prevent flex blowouts */
        display: flex;
        flex-direction: column;
        position: relative;
        overflow: hidden;
    }
</style>
