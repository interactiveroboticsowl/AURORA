<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { Project } from '$lib/project.svelte';
	import type { LayoutData } from './$types';

	interface LayoutProps {
		children: Snippet;
		data: LayoutData;
	}

	let { children, data }: LayoutProps = $props();
	let projects: Project[] = data.projects as Project[];
</script>

{@render children()}
