<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import type { Item } from '$lib/components/survey/schemaGenerator';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import * as RadioGroup from '$lib/components/ui/radio-group';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Label } from '$lib/components/ui/label';

	interface Props {
		form;
		item: Item;
		value: string | string[];
		isMultiple: boolean;
	}

	let { form, item, value = $bindable(), isMultiple }: Props = $props();
</script>

<Card.Root class="mx-2">
	<Form.Field {form} name={`item_${item.id}`}>
		<Form.Control let:attrs>
			<Card.Header>
				<Card.Title>{item.title}</Card.Title>
				{#if item.prompt}
					<Card.Description>{item.prompt}</Card.Description>
				{/if}
			</Card.Header>
			<Card.Content>
				{#if isMultiple}
					<div class="space-y-2">
						{#each item.options || [] as option, index}
							<div class="flex items-center space-x-2">
								<Checkbox
									id={`item_${item.id}_option_${index}`}
									checked={Array.isArray(value) && value.includes(option)}
									onCheckedChange={(isChecked) => {
										if (isChecked) {
											value = [...(value || []), option];
										} else {
											value = value.filter((ans) => ans !== option);
										}
									}}
									{...attrs}
								/>
								<Label for={`item_${item.id}_option_${index}`}>{option}</Label>
							</div>
						{/each}
					</div>
				{:else}
					<RadioGroup.Root bind:value {...attrs}>
						{#each item.options || [] as option, index}
							<div class="flex items-center space-x-2">
								<RadioGroup.Item value={option} id={`item_${item.id}_option_${index}`} />
								<Label for={`item_${item.id}_option_${index}`}>{option}</Label>
							</div>
						{/each}
					</RadioGroup.Root>
				{/if}
			</Card.Content>
		</Form.Control>
		<Form.FieldErrors />
	</Form.Field>
</Card.Root>
