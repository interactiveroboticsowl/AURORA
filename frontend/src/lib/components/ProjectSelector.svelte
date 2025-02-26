<script lang="ts">
	import type { Project } from '$lib/project.svelte';
	import { Button } from './ui/button';
	import * as Popover from '$lib/components/ui/popover/index.js';
	import * as Command from '$lib/components/ui/command/index.js';
	import { ChevronsUpDown, FilePlus2 } from 'lucide-svelte';
	import { tick } from 'svelte';
	import { goto } from '$app/navigation';

	interface Props {
		projects: Project[];
		currentProject?: Project;
	}
	let { projects, currentProject }: Props = $props();
	let open: boolean = $state(false);
	function closeAndFocusTrigger(triggerId: string) {
		open = false;
		tick().then(() => {
			document.getElementById(triggerId)?.focus();
		});
	}
</script>

<Popover.Root bind:open let:ids portal={null}>
	<Popover.Trigger asChild let:builder>
		<Button
			builders={[builder]}
			variant="outline"
			role="combobox"
			aria-expanded={open}
			class="w-[200px] justify-between"
		>
			{#if currentProject}
				{currentProject.name}
			{:else}
				Select a project
			{/if}
			<ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
		</Button>
	</Popover.Trigger>
	<Popover.Content aria-labelledby={ids.trigger} class="w-[200px] p-2">
		<Command.Root>
			<Command.Input placeholder="Search projects" />
			<Command.Empty>No projects found</Command.Empty>
			<Command.Group>
				{#each projects as project (project.id)}
					<Command.Item
						onclick={() => {
							closeAndFocusTrigger(ids.trigger);
							goto(`/projects/${project.id}`);
						}}
					>
						{project.name}
					</Command.Item>
				{/each}
			</Command.Group>
			<Command.Separator />
			<Command.Item>
				<Button
					variant="ghost"
					href="/projects"
					onclick={() => closeAndFocusTrigger(ids.trigger)}
					class="text-center"
				>
					<FilePlus2 class="mr-2 h-4 w-4" />
					Create new</Button
				>
			</Command.Item>
		</Command.Root>
	</Popover.Content>
</Popover.Root>
