<script lang="ts">
	import ProjectNav from '$lib/components/ProjectNav.svelte';
	import type { LayoutData } from './$types';
	import ProjectSelector from '$lib/components/ProjectSelector.svelte';
	import { Separator } from '$lib/components/ui/separator';
	import * as Resizable from '$lib/components/ui/resizable/index.js';
	import type { Snippet } from 'svelte';
	import { Edit } from 'lucide-svelte';

	interface Props {
		data: LayoutData;
		children: Snippet;
	}

	let { data, children }: Props = $props();

	let { projects, currentProject } = $derived(data);
</script>

<Resizable.PaneGroup direction="horizontal" class="h-screen items-stretch">
	<Resizable.Pane defaultSize={20} minSize={15} maxSize={25} class="h-screen">
		<div class="flex h-[52px] items-center justify-between px-4">
			<ProjectSelector {projects} {currentProject} />
			<a
				href="/item-manager"
				class="ml-4 text-primary hover:text-accent transition-colors duration-200"
				title="Manage Items"
			>
				<Edit class="w-6 h-6 hover:text-accent transition-colors duration-200" />
			</a>
		</div>
		<Separator />
		<div class="h-[calc(100vh-52px)]">
			<ProjectNav />
		</div>
	</Resizable.Pane>

	<Resizable.Handle withHandle />
	{#if children}
		{@render children()}
	{:else}
		<Resizable.Pane></Resizable.Pane>
	{/if}
</Resizable.PaneGroup>
