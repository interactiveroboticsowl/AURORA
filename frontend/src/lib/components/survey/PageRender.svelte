<script lang="ts">
	import { superForm } from 'sveltekit-superforms';
	import { zod } from 'sveltekit-superforms/adapters';
	import * as Form from '$lib/components/ui/form/index.js';
	import {
		FreeTextItem,
		MultipleChoiceItem,
		ScaleItem,
		MatrixScaleItem,
		StaticTextItem,
		VideoItem,
		ImageItem
	} from '$lib/components/survey/render_components';
	import { generateSchemaForPage, type Page } from '$lib/components/survey/schemaGenerator';
	import SuperDebug from 'sveltekit-superforms';
	import { dev } from '$app/environment';
	import { invalidate } from '$app/navigation';
	import { page as pageStore } from '$app/stores';

	interface Props {
		pageForm: any;
		page: Page;
		preview?: boolean;
		prevPageId: number;
		nextPageId: number;
	}

	let { page, pageForm, prevPageId, nextPageId }: Props = $props();

	const pageSchema = generateSchemaForPage(page);

	const form = superForm(pageForm, {
		validators: zod(pageSchema),
		dataType: 'json',
		resetForm: true
	});

	const { form: formData, enhance, submitting } = form;
</script>

<form method="POST" use:enhance action="?/updateAnswers" class="space-y-4">
	{#each page.items as pageItem}
		{#if pageItem.item_type == 'question'}
			{#if pageItem.question_type == 'free_text'}
				<FreeTextItem item={pageItem} {form} bind:value={$formData[`item_${pageItem.id}`].answer} />
			{:else if pageItem.question_type?.startsWith('multiple_choice')}
				<MultipleChoiceItem
					item={pageItem}
					{form}
					bind:value={$formData[`item_${pageItem.id}`].answer}
					isMultiple={pageItem.question_type == 'multiple_choice_multiple'}
				/>
			{:else if pageItem.question_type == 'scale'}
				<ScaleItem item={pageItem} {form} bind:value={$formData[`item_${pageItem.id}`].answer} />
			{:else if pageItem.question_type == 'matrix_scale'}
				<MatrixScaleItem
					item={pageItem}
					{form}
					bind:value={$formData[`item_${pageItem.id}`].answer}
				/>
			{/if}
		{:else if pageItem.item_type == 'static_text'}
			<StaticTextItem item={pageItem} />
		{:else if pageItem.item_type == 'video'}
			<VideoItem item={pageItem} />
		{:else if pageItem.item_type == 'image'}
			<ImageItem item={pageItem} />
		{/if}
	{/each}

	<div class="justify-between flex-row w-full flex my-2 px-4">
		<div>
			{#if !page.back_button_disabled && prevPageId}
				<Form.Button type="submit" name="navigation" value={prevPageId} disabled={$submitting}>
					Back
				</Form.Button>
			{/if}
		</div>

		<div>
			{#if nextPageId}
				<Form.Button type="submit" name="navigation" value={nextPageId} disabled={$submitting}>
					Next
				</Form.Button>
			{:else}
				<Form.Button type="submit" name="navigation" value="finish" disabled={$submitting}>
					Submit
				</Form.Button>
			{/if}
		</div>
	</div>

	<!-- <SuperDebug data={$formData} display={dev} /> -->
</form>
