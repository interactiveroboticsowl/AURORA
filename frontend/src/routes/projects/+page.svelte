<script lang="ts">
	import { goto } from '$app/navigation';
	import { ChevronsUpDown } from 'lucide-svelte';
	import { tick } from 'svelte';
	import * as Command from '$lib/components/ui/command';
	import * as Popover from '$lib/components/ui/popover';
	import { Button } from '$lib/components/ui/button';
	import ProjectForm from '../../lib/components/forms/project/ProjectForm.svelte';
	import type { PageData } from './$types';
	import type { Project } from '$lib/project.svelte';

	let { data } = $props<{ data: PageData }>();
	let { form, projects } = data;

	let open = $state(false);
	let value = $state('');
	let showNewProjectForm = $state(false);
	let search = $state('');

	let selectedValue = $derived(
		projects.find((p: Project) => p.name === value)?.name ?? 'Select a project...'
	);

	let filteredProjects = $derived(
		projects.filter((project: Project) => project.name.startsWith(search))
	);

	function closeAndFocusTrigger(triggerId: string) {
		open = false;
		tick().then(() => {
			document.getElementById(triggerId)?.focus();
		});
	}

	function handleCreateNew() {
		showNewProjectForm = true;
	}
</script>

<div class="space-y-6 p-6">
	<Popover.Root bind:open let:ids>
		<Popover.Trigger asChild let:builder>
			<Button
				builders={[builder]}
				variant="outline"
				role="combobox"
				aria-expanded={open}
				class="w-full justify-between"
			>
				{selectedValue}
				<ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
			</Button>
		</Popover.Trigger>
		<Popover.Content class="p-0">
			<Command.Root>
				<Command.Input bind:value={search} placeholder="Search projects..." />
				<Command.Empty>No project found.</Command.Empty>
				<Command.Group>
					{#each filteredProjects as project (project.id)}
						<a href={`/projects/${project.id}`}>
							<Command.Item>
								{project.name}
							</Command.Item>
						</a>
					{/each}
				</Command.Group>
			</Command.Root>
		</Popover.Content>
	</Popover.Root>

	<div class="flex justify-center">
		<Button on:click={handleCreateNew}>Create New Project</Button>
	</div>

	{#if showNewProjectForm}
		<div class="mt-6">
			<h2 class="text-lg font-semibold mb-4">Create New Project</h2>
			<ProjectForm data={form} />
		</div>
	{/if}
</div>
