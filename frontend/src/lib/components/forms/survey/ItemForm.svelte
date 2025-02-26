<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import * as Select from '$lib/components/ui/select/index.js';
	import * as Table from '$lib/components/ui/table';
	import QuillEditor from '$lib/components/QuillEditor.svelte';
	import 'quill/dist/quill.snow.css';
	import { type ItemSchema, itemSchema } from '$lib/components/forms/survey/schema';
	import { type SuperValidated, superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import SuperDebug from 'sveltekit-superforms';
	import { ITEM_TYPES, QUESTION_TYPES } from '$lib/components/forms/survey/enums';
	import { Button } from '$lib/components/ui/button';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import { TrashIcon } from 'lucide-svelte';
	import * as flashModule from 'sveltekit-flash-message/client';
	import {
		type ItemType,
		itemType,
		type QuestionType,
		questionType
	} from '$lib/components/forms/item-template/schema';
	import { dev } from '$app/environment';

	interface Props {
		data: SuperValidated<ItemSchema>;
	}

	let { data }: Props = $props();
	let form = superForm(data, {
		validators: zodClient(itemSchema),
		dataType: 'json',
		syncFlashMessage: true,
		resetForm: false,
		flashMessage: { module: flashModule },
		onError: 'apply',
		onUpdated({ form }) {
			if (!data.data.id && form.valid) {
				reset({ keepMessage: true });
			}
		}
	});

	const capitalize = (str: string) => str.charAt(0).toUpperCase() + str.slice(1);
	const { form: formData, enhance, reset } = form;

	let selectedItemType = $derived.by(() => {
		return $formData.item_type
			? { value: $formData.item_type, label: capitalize($formData.item_type) }
			: undefined;
	});

	let selectedQuestionType = $derived.by(() => {
		return $formData.question_type
			? {
					value: $formData.question_type,
					label: capitalize($formData.question_type).replace('_', ' ')
				}
			: undefined;
	});
	function resetQuestionFields() {
		$formData.options = undefined;
		$formData.scale_min = undefined;
		$formData.scale_max = undefined;
		$formData.matrix_options = undefined;
		$formData.statements = undefined;
	}

	function initializeQuestionFields(type: QuestionType) {
		resetQuestionFields();
		switch (type) {
			case 'multiple_choice_single':
				$formData.options = [];
				break;
			case 'multiple_choice_multiple':
				$formData.options = [];
				break;
			case 'scale':
				$formData.scale_min = 1;
				$formData.scale_max = 5;
				break;
			case 'matrix_scale':
				$formData.matrix_options = [];
				$formData.statements = [];
				break;
		}
	}
</script>

<div class="flex flex-col h-full">
	<ScrollArea class="flex-grow">
		<form method="POST" use:enhance>
			<Form.Field {form} name="title">
				<Form.Control let:attrs>
					<Form.Label>Title</Form.Label>
					<Input bind:value={$formData.title} {...attrs} placeholder="Item Title" />
				</Form.Control>
				<Form.Description>Please enter the title of the item</Form.Description>
				<Form.FieldErrors />
			</Form.Field>

			<Form.Field {form} name="prompt">
				<Form.Control let:attrs>
					<Form.Label>Prompt</Form.Label>
					<Textarea bind:value={$formData.prompt as string} {...attrs} placeholder="Item Prompt" />
				</Form.Control>
				<Form.Description>Please enter the prompt for the item (optional)</Form.Description>
				<Form.FieldErrors />
			</Form.Field>

			<div class="grid grid-cols-2 space-x-2">
				<Form.Field {form} name="item_type">
					<Form.Control let:attrs>
						<Form.Label>Item Type</Form.Label>
						<Select.Root
							selected={selectedItemType}
							onSelectedChange={(v) => {
								if (v && itemType.parse(v.value)) {
									const newItemType = v.value as ItemType;
									$formData.item_type = newItemType;
									if (v.value !== 'question') {
										$formData.question_type = undefined;
										resetQuestionFields();
									}
								}
							}}
							portal={null}
						>
							<Select.Trigger {...attrs}>
								<Select.Value placeholder="Select item type" />
							</Select.Trigger>
							<Select.Content>
								{#each ITEM_TYPES as type}
									{@const Icon = type.icon}
									<Select.Item value={type.value}>
										<div class="flex items-start gap-2">
											<div class="text-muted-foreground my-auto">
												<Icon class="size-4" />
											</div>
											<p>{type.label}</p>
										</div>
									</Select.Item>
								{/each}
							</Select.Content>
						</Select.Root>
					</Form.Control>
					<Form.FieldErrors />
				</Form.Field>

				{#if $formData.item_type === 'question'}
					<Form.Field {form} name="question_type">
						<Form.Control let:attrs>
							<Form.Label>Question Type</Form.Label>
							<Select.Root
								selected={selectedQuestionType}
								onSelectedChange={(v) => {
									if (v && questionType.parse(v.value)) {
										const newQuestionType = v.value as QuestionType;
										$formData.question_type = newQuestionType;
										initializeQuestionFields(newQuestionType);
									}
								}}
								portal={null}
							>
								<Select.Trigger {...attrs}>
									<Select.Value placeholder="Select question type" />
								</Select.Trigger>
								<Select.Content>
									<Select.Group>
										<Select.Label>Question Types</Select.Label>
										{#each QUESTION_TYPES as type}
											<Select.Item value={type.value}>{type.label}</Select.Item>
										{/each}
									</Select.Group>
								</Select.Content>
							</Select.Root>
						</Form.Control>
						<Form.FieldErrors />
					</Form.Field>
				{/if}
			</div>

			{#if $formData.item_type === 'question' && $formData.question_type && $formData.question_type.startsWith('multiple_choice')}
				<Form.Field {form} name="options">
					<Form.Control let:attrs>
						<Form.Label>Options</Form.Label>
						<div class="space-y-2">
							{#each $formData.options || [] as _, index}
								<div class="flex items-center space-x-2">
									<Input
										type="text"
										bind:value={($formData.options as string[])[index]}
										placeholder={`Option ${index + 1}`}
										{...attrs}
									/>
									<Button
										type="button"
										variant="outline"
										size="icon"
										on:click={() => {
											$formData.options = ($formData.options || []).filter((_, i) => i !== index);
										}}
									>
										<TrashIcon class="h-4 w-4" />
									</Button>
								</div>
							{/each}
							<Button
								type="button"
								variant="outline"
								on:click={() => {
									$formData.options = [...($formData.options || []), ''];
								}}
							>
								Add Option
							</Button>
						</div>
					</Form.Control>
					<Form.Description>Add or remove options as needed</Form.Description>
					<Form.FieldErrors />
				</Form.Field>
			{/if}

			{#if $formData.item_type === 'question' && $formData.question_type === 'scale'}
				<div class="grid grid-cols-2 space-x-2">
					<Form.Field {form} name="scale_min">
						<Form.Control let:attrs>
							<Form.Label>Scale Minimum</Form.Label>
							<Input type="number" bind:value={$formData.scale_min} {...attrs} />
						</Form.Control>
						<Form.FieldErrors />
					</Form.Field>

					<Form.Field {form} name="scale_max">
						<Form.Control let:attrs>
							<Form.Label>Scale Maximum</Form.Label>
							<Input type="number" bind:value={$formData.scale_max} {...attrs} />
						</Form.Control>
						<Form.FieldErrors />
					</Form.Field>
				</div>
			{/if}
			{#if $formData.item_type === 'question' && $formData.question_type === 'matrix_scale'}
				<Form.Field {form} name="matrix_options">
					<Form.Control let:attrs>
						<Form.Label>Scale Options</Form.Label>
						<div class="space-y-2">
							{#each $formData.matrix_options || [] as option, index}
								<div class="flex items-center space-x-2">
									<Input
										type="text"
										bind:value={($formData.matrix_options as string[])[index]}
										placeholder={`Option ${index + 1}`}
										{...attrs}
									/>
									<Button
										type="button"
										variant="outline"
										size="icon"
										on:click={() => {
											$formData.matrix_options = ($formData.matrix_options || []).filter(
												(_, i) => i !== index
											);
										}}
									>
										<TrashIcon class="h-4 w-4" />
									</Button>
								</div>
							{/each}
							<Button
								type="button"
								variant="outline"
								on:click={() => {
									$formData.matrix_options = [...($formData.matrix_options || []), ''];
								}}
							>
								Add Scale Option
							</Button>
						</div>
					</Form.Control>
					<Form.Description>Add or remove scale options as needed</Form.Description>
					<Form.FieldErrors />
				</Form.Field>

				<Form.Field {form} name="statements">
					<Form.Control let:attrs>
						<Form.Label>Statements</Form.Label>
						<div class="space-y-2">
							{#each $formData.statements as string[] as statement, index}
								<div class="flex items-center space-x-2">
									<Input
										type="text"
										bind:value={($formData.statements as string[])[index]}
										placeholder={`Statement ${index + 1}`}
										{...attrs}
									/>
									<Button
										type="button"
										variant="outline"
										size="icon"
										on:click={() => {
											$formData.statements = ($formData.statements || []).filter(
												(_, i) => i !== index
											);
										}}
									>
										<TrashIcon class="h-4 w-4" />
									</Button>
								</div>
							{/each}
							<Button
								type="button"
								variant="outline"
								on:click={() => {
									$formData.statements = [...($formData.statements || []), ''];
								}}
							>
								Add Statement
							</Button>
						</div>
					</Form.Control>
					<Form.Description>Add or remove statements as needed</Form.Description>
					<Form.FieldErrors />
				</Form.Field>
				<div class="mt-4">
					<h3 class="text-lg font-semibold mb-2">Matrix Preview</h3>
					<Table.Root>
						<Table.Caption>Matrix Scale Question Preview</Table.Caption>
						<Table.Header>
							<Table.Row>
								<Table.Head class="w-[200px]">Statements</Table.Head>
								{#each $formData.matrix_options as string[] as option}
									<Table.Head>{option}</Table.Head>
								{/each}
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#each $formData.statements as string[] as statement}
								<Table.Row>
									<Table.Cell class="font-medium">{statement}</Table.Cell>
									{#each $formData.matrix_options as string[] as option}
										<Table.Cell>
											<Input class="w-[12px]" type="radio" disabled />
										</Table.Cell>
									{/each}
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			{/if}
			{#if $formData.item_type === 'image'}
				<Form.Field {form} name="image_url">
					<Form.Control let:attrs>
						<Form.Label>Image URL</Form.Label>
						<Input bind:value={$formData.image_url} {...attrs} placeholder="Image URL" />
					</Form.Control>
					<Form.Description>Please enter the URL of the image</Form.Description>
					<Form.FieldErrors />
				</Form.Field>
			{/if}

			{#if $formData.item_type === 'video'}
				<Form.Field {form} name="video_url">
					<Form.Control let:attrs>
						<Form.Label>Video URL</Form.Label>
						<Input bind:value={$formData.video_url} {...attrs} placeholder="Video URL" />
					</Form.Control>
					<Form.Description>Please enter the URL of the video</Form.Description>
					<Form.FieldErrors />
				</Form.Field>
			{/if}

			{#if $formData.item_type === 'static_text'}
				<Form.Field {form} name="text_content">
					<Form.Control let:attrs>
						<Form.Label>Text Content</Form.Label>
						<QuillEditor
							value={$formData.text_content as string}
							onChange={(content) => ($formData.text_content = content)}
						/>
					</Form.Control>
					<Form.Description>Please enter the static text content</Form.Description>
					<Form.FieldErrors />
				</Form.Field>
			{/if}

			<Form.Button>Submit</Form.Button>
		</form>
		<!-- <SuperDebug data={$formData} display={dev} /> -->
	</ScrollArea>
</div>
