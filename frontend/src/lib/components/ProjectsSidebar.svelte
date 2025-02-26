<script lang="ts">
	import * as Select from '$lib/components/ui/select/index.js';
	import type { Project } from '$lib/project.svelte';

	interface Props {
		projects: Project[];
		currentProject?: Project;
	}

	let { projects, currentProject }: Props = $props();
</script>

<Select.Root portal={null} selected={{ value: currentProject.id, label: currentProject.name }}>
	<Select.Trigger aria-label="Select project">
		<span>
			{currentProject.name}
		</span>
	</Select.Trigger>
	<Select.Content sameWidth={true}>
		<Select.Group>
			{#each projects as project (project.id)}
				<Select.Item value={project.id} label={project.name}>
					{project.name}
				</Select.Item>
			{/each}
		</Select.Group>
	</Select.Content>
	<Select.Input hidden name="project" />
</Select.Root>
