<script lang="ts">
    import { page } from '$app/stores';
    import { PlusCircle, List, Database } from 'lucide-svelte';
    import { cn } from '$lib/utils';
    import { derived } from 'svelte/store';
    import Sun from 'lucide-svelte/icons/sun';
	import Moon from 'lucide-svelte/icons/moon';
    import { toggleMode } from 'mode-watcher';
	import { Button } from '$lib/components/ui/button/index.js';

    let currentPath = derived(page, ($page) => $page.url.pathname);

    const navItems = [
        { name: 'Create Item', path: '/item-manager/create', icon: PlusCircle },
        { name: 'Manage Items', path: '/item-manager/manage', icon: List },
        { name: 'Data', path: '/item-manager/data', icon: Database }
    ];
</script>

<nav class="bg-card text-card-foreground p-4 space-y-2 w-64 h-full overflow-y-auto flex flex-col shadow-lg">
    <div class="flex-grow">
        {#each navItems as item}
            <a
                href={item.path}
                class={cn(
                    'flex items-center px-4 py-2 rounded-lg hover:bg-muted hover:text-muted-foreground transition-all duration-200',
                    $currentPath === item.path && 'bg-primary text-primary-foreground font-bold'
                )}
            >
                <span class="mr-2">
                    <svelte:component this={item.icon} class="w-5 h-5 text-muted-foreground" />
                </span>

                <span class="text-lg">{item.name}</span>
            </a>
        {/each}
    </div>
    <div class="mt-auto pt-4">
		<Button on:click={toggleMode} variant="outline" size="icon" class="w-full justify-center">
			<Sun
				class="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
			/>
			<Moon
				class="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
			/>
			<span class="sr-only">Toggle theme</span>
		</Button>
	</div>
</nav>