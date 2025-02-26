<script lang="ts">
	import '$lib/css/surveyTheme.css';
	import type { PageData } from './$types';
	import PageRender from '$lib/components/survey/PageRender.svelte';

	let { data } = $props<{ data: PageData }>();

	const { pageData, form, nextPageId, prevPageId } = $derived(data);
</script>

{#key pageData.id}
	<PageRender page={pageData} pageForm={form} {nextPageId} {prevPageId} />
{/key}
