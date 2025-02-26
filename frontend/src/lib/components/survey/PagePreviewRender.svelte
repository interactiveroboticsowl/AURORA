<script lang="ts">
	import { superForm, defaults } from 'sveltekit-superforms';
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
	import { generateSchemaForPage } from '$lib/components/survey/schemaGenerator';

	let { page, participant_id, preview = false, changePage, isFirst, isLast } = $props();

	const pageSchema = generateSchemaForPage(page);

	const form = superForm(
		defaults({ page_id: page.id, participant_id: participant_id }, zod(pageSchema)),
		{
			validators: zod(pageSchema),
			dataType: 'json',
			resetForm: false,
			SPA: preview
		}
	);

	const { form: formData, enhance, errors } = form;
</script>

<form method="POST" use:enhance class="space-y-4">
	{#each page.items as pageItem}
		{#if pageItem.item_type == 'question'}
			{#if pageItem.question_type == 'free_text'}
				<FreeTextItem item={pageItem} {form} bind:value={$formData[`item_${pageItem.id}`].answer} />
			{:else if pageItem.question_type.startsWith('multiple_choice')}
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
			{#if !page.back_button_disabled && !isFirst}
				<Form.Button onclick={() => changePage(-1)}>Back</Form.Button>
			{/if}
		</div>
		<div>
			{#if !isLast}
				<Form.Button onclick={() => changePage(1)}>Next</Form.Button>
			{/if}
		</div>
	</div>
</form>
