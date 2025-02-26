<script lang="ts">
	import PagePreviewRender from '$lib/components/survey/PagePreviewRender.svelte';
	import '$lib/css/surveyTheme.css';

	let { pages, participant_id, preview = false } = $props();
	let currentPage = $state(0);
	let maxPage = pages[pages.length - 1].order;
	let firstPage = pages[0];

	function changePage(value: number) {
		currentPage += value;
	}
	let page = $derived(pages[currentPage]);
</script>

<div class="theme-root">
	{#key currentPage}
		<PagePreviewRender
			{page}
			{participant_id}
			{changePage}
			{preview}
			isFirst={page.order == firstPage.order}
			isLast={page.order == maxPage}
		/>
	{/key}
</div>

