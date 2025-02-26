<script lang="ts">
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import { page } from '$app/stores';
	import { Waypoints, Database, BookOpenText, PanelsTopLeft, ChevronDown } from 'lucide-svelte';
	import { cn } from '$lib/utils';
	import Sun from 'lucide-svelte/icons/sun';
	import Moon from 'lucide-svelte/icons/moon';
	import { toggleMode } from 'mode-watcher';
	import { Button } from '$lib/components/ui/button/index.js';
	import { signOut } from '@auth/sveltekit/client';
	let currentPath = $derived($page.url.pathname);
	let projectId = $derived($page.params.projectId);
	const navItems = $derived([
		{ name: 'Dashboard', path: `/projects/${projectId}`, icon: PanelsTopLeft },
		{
			name: 'Simulation',
			path: `/projects/${projectId}/simulation`,
			subItems: [
				// { name: 'Overview', path: `/projects/${projectId}/simulation` },				
			],
			icon: Waypoints
		},
		{ name: 'Survey', path: `/projects/${projectId}/survey`, icon: BookOpenText },
		{ name: 'Data', path: `/projects/${projectId}/data`, icon: Database }
	]);
	function isSubItemActive(item) {
		if (!item.subItems) return false;
		return item.subItems.some(
			(subItem) => currentPath === subItem.path || currentPath.startsWith(subItem.path)
		);
	}
</script>

<nav
	class="sidebar bg-card text-card-foreground p-4 space-y-2 w-64 h-full overflow-y-auto flex flex-col"
>
	<div class="flex-grow">
		{#each navItems as item}
			{#if item.subItems && item.subItems.length > 0}
				<Collapsible.Root open={isSubItemActive(item)}>
					<Collapsible.Trigger
						class={cn(
							'flex items-center px-4 py-2 rounded-lg hover:bg-muted hover:text-muted-foreground transition-all duration-200',
							(currentPath.startsWith(item.path) || isSubItemActive(item)) &&
								'bg-primary text-primary-foreground font-bold'
						)}
					>
						<div class="flex items-center">
							<span class="mr-2">
								<svelte:component this={item.icon} />
							</span>
							<span>{item.name}</span>
						</div>
						<ChevronDown />
					</Collapsible.Trigger>
					<Collapsible.Content>
						<div class="ml-6 mt-2 space-y-2">
							{#each item.subItems as subItem}
								<a
									href={subItem.path}
									class={cn(
										'block px-4 py-2 rounded-lg hover:bg-muted transition-colors',
										currentPath === subItem.path &&
											'bg-secondary text-secondary-foreground font-semibold'
									)}
								>
									{subItem.name}
								</a>
							{/each}
						</div>
					</Collapsible.Content>
				</Collapsible.Root>
			{:else}
				<a
					href={item.path}
					class={cn(
						'flex items-center px-4 py-2 rounded-lg hover:bg-muted hover:text-muted-foreground transition-all duration-200',
						currentPath === item.path && 'bg-primary text-primary-foreground font-bold'
					)}
				>
					<span class="mr-2">
						<svelte:component this={item.icon} />
					</span>
					<span>{item.name}</span>
				</a>
			{/if}
		{/each}
	</div>
	<div class="w-full mt-auto grid grid-cols-2 gap-2">
		<Button on:click={toggleMode} variant="outline" class="w-full justify-center">
			<Sun
				class="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
			/>
			<Moon
				class="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
			/>
			<span class="sr-only">Toggle theme</span>
		</Button>
		{#if $page.data.session}
			<Button on:click={() => signOut()} variant="outline" class="w-full justify-center">
				Sign out
			</Button>
		{/if}
	</div>
</nav>
