<script lang="ts">
    import type { Snippet } from "svelte";

    let { sidebar, children } = $props<{
        sidebar: Snippet;
        children: Snippet;
    }>();
</script>

<div class="app-layout">
    <div class="sidebar-wrapper">
        {@render sidebar()}
    </div>
    <main class="main-content">
        <div class="main-inner">
            {@render children()}
        </div>
    </main>
</div>

<style>
    .app-layout {
        display: flex;
        width: 100%;
        height: 100vh;
        overflow: hidden;
        background: #f9fafb;
    }

    .sidebar-wrapper {
        flex-shrink: 0;
        height: 100%;
        z-index: 10;
    }

    .main-content {
        flex-grow: 1;
        height: 100%;
        overflow-y: auto;
        position: relative;
    }

    .main-inner {
        padding: 2rem;
        max-width: 1000px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }
</style>
