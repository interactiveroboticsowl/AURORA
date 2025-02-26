<script lang="ts">
	import * as Resizable from '$lib/components/ui/resizable/index.js';
	import { Separator } from '$lib/components/ui/separator';
	import { Button } from '$lib/components/ui/button';
	import type { LayoutData } from './$types';
	import SurveyPage from '$lib/components/survey/SurveyPage.svelte';
	import type { Snippet } from 'svelte';
	import { page } from '$app/stores';
	import { invalidate } from '$app/navigation';
	import { API_BASE_URL } from '$lib/config';

	let { data, children } = $props<{ data: LayoutData; children: Snippet }>();
	console.log('data:', data);

	let projectId: string | undefined;

    page.subscribe(($page) => {
        projectId = $page.params.projectId;
    });

	async function movePage(pageId: number, direction: 'up' | 'down') {
		let pages = data.survey.pages;
		let pageToEdit = pages.find((page) => page.id === pageId);
		let wantedOrder = pageToEdit.order + (direction === 'up' ? -1 : 1);
		if (wantedOrder < 0 || wantedOrder > pages.length) {
			return;
		}
		let blockingPage = pages.find((page) => page.order === wantedOrder);
		pageToEdit.order = wantedOrder;
		blockingPage.order = pageToEdit.order + (direction === 'up' ? 1 : -1);

		pages = pages.sort((a, b) => a.order - b.order);

		const updatedPageOrder = pages.map((page) => ({ id: page.id, order: page.order }));

		const response = await fetch(
			`/projects/${$page.params.projectId}/survey/api?action=reorderPage`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ pageOrder: updatedPageOrder })
			}
		);

		if (!response.ok) {
			const errorText = await response.text();
			console.error('Failed to reorder pages:', errorText);
		}

		invalidate('project:survey');
	}

	async function deletePage(pageId: number) {
		let pages = data.survey.pages;
		const pageIndex = pages.findIndex((page) => page.id === pageId);
		if (pageIndex === -1) return;

		// Update the local state by removing the page
		pages.splice(pageIndex, 1);

		// Perform API call to delete the page
		const response = await fetch(`/projects/${$page.params.projectId}/survey/api?action=deletePage`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ pageId }),
		});

		if (!response.ok) {
			const errorText = await response.text();
			console.error('Failed to delete page:', errorText);
		}

		invalidate('project:survey');
	}


	async function deleteItem(pageId: number, itemId: number) {
		const pageIndex = data.survey.pages.findIndex((page) => page.id === pageId);
		console.log('pageIndex:', pageIndex);

		if (pageIndex === -1) {
			console.error(`Page with ID ${pageId} not found in data.survey.pages.`);
			return;
		}

		const page = data.survey.pages[pageIndex];
		console.log('Page found:', page);

		if (!Array.isArray(page.items)) {
			console.error(`Items array not found for page with ID ${pageId}.`);
			return;
		}

		const itemIndex = page.items.findIndex((item) => item.id === itemId);
		console.log('itemIndex:', itemIndex);

		if (itemIndex === -1) {
			console.error(`Item with ID ${itemId} not found in page with ID ${pageId}.`);
			return;
		}

		console.log('Removing item:', page.items[itemIndex]);
		page.items.splice(itemIndex, 1);

		const response = await fetch(`/projects/${projectId}/survey/api?action=deleteItem`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ pageId, itemId }),
		});

		if (!response.ok) {
			const errorText = await response.text();
			console.error('Failed to delete item:', errorText);
		}

		invalidate('project:survey');
	}


	async function reorderItem(pageId: number, itemId: number, direction: 'up' | 'down') {
		const pageIndex = data.survey.pages.findIndex((page) => page.id === pageId);
		if (pageIndex === -1) {
			console.error(`Page with ID ${pageId} not found in data.survey.pages.`);
			return;
		}

		const page = data.survey.pages[pageIndex];
		const itemIndex = page.items.findIndex((item) => item.id === itemId);
		if (itemIndex === -1) {
			console.error(`Item with ID ${itemId} not found in page with ID ${pageId}.`);
			return;
		}

		const itemToEdit = page.items[itemIndex];
		const newOrder = direction === 'up' ? itemToEdit.order - 1 : itemToEdit.order + 1;

		if (newOrder < 0 || newOrder >= page.items.length) {
			console.warn('Cannot move item further in the specified direction.');
			return;
		}

		const blockingItem = page.items.find((item) => item.order === newOrder);
		if (!blockingItem) {
			console.error('Blocking item not found in the specified order.');
			return;
		}


		blockingItem.order = itemToEdit.order;
		itemToEdit.order = newOrder;


		page.items = page.items.sort((a, b) => a.order - b.order);

		const updatedItemOrders = page.items.map((item) => ({ id: item.id, order: item.order }));


		const response = await fetch(`/projects/${projectId}/survey/api?action=reorderItem`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ pageId, updatedItemOrders }),
		});


		if (!response.ok) {
			const errorText = await response.text();
			console.error('Failed to reorder items:', errorText);
		}


		invalidate('project:survey');
	}


</script>

<Resizable.Pane>
	<div class="flex h-[52px] items-center">
		<h1 class="text-2xl font-bold pl-2">
			Survey{data.survey ? ` - ${data.survey.title}` : ''}
		</h1>
	</div>
	<Separator />
	{#if data.survey}
		{#each data.survey.pages as survey_page, index (survey_page.id ?? index)}
			<SurveyPage
				data={survey_page}
				isFirst={index === 0}
				isLast={index === data.survey.pages.length - 1}
				{movePage}
				{deletePage}
				{deleteItem}
				{reorderItem}
			/>
		{/each}
		<div class="flex flex-col mx-4">
			<Separator class="" />
			<div class="flex mt-4 justify-center items-center space-x-2">
				<Button class="" href={`/projects/${$page.params.projectId}/survey/preview`}>Preview</Button
				>
				<Button class="" href={`/projects/${$page.params.projectId}/survey/pages`}>Add Page</Button>
			</div>
			<div class="text-yellow-600">
				<span class="font-semibold block">Note:</span>
				Avoid editing surveys in published projects unless you know what you are doing, as it may impact responses and can result in data loss.
			</div>
		</div>
	{:else}
		<div class="flex flex-col items-center justify-center h-full space-y-4">
			<h4>No survey created for this project yet</h4>
		</div>
	{/if}
</Resizable.Pane>
<Resizable.Handle withHandle />
<Resizable.Pane>
	{#if children}
		{@render children()}
	{/if}
</Resizable.Pane>
