<script lang="ts">
	import '$lib/css/surveyTheme.css';
	import type { LayoutData } from './$types';
	import { cn } from '$lib/utils';
	import ApplicationComponent from '$lib/components/ApplicationComponent.svelte';
	import type { Snippet } from 'svelte';
	import { page } from '$app/stores';

	let { data, children } = $props<{ data: LayoutData; children: Snippet }>();

	const { routes, survey } = $derived(data);

	let currentPageIndex = $derived(Number($page.params.pageId) - 1);
	let shouldShowApplication = $derived(
		survey && currentPageIndex !== undefined
			? survey.pages[currentPageIndex].application_enabled
			: true
	);
	let isSingleColumn = $derived(survey ? !shouldShowApplication : true);
</script>

<div
	class={cn(
		'grid theme-root h-screen w-screen bg-background gap-4',
		isSingleColumn ? 'grid-cols-2 ' : 'p-4 grid-cols-3'
	)}
>
	{#if shouldShowApplication}
		<div class="rounded-lg col-span-2 h-full">
			<ApplicationComponent endpoint={routes.endpoints[0]} />
		</div>
	{/if}
	{#if survey}
		<div class={cn('', isSingleColumn ? 'w-[45%] col-span-2 mx-auto mt-8' : 'w-full')}>
			{@render children()}
		</div>
	{/if}
</div>
