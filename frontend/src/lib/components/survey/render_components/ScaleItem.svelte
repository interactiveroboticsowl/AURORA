<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import type { Item } from '$lib/components/survey/schemaGenerator';
	import { Slider } from '$lib/components/ui/slider/index.js';
	import * as Card from '$lib/components/ui/card/index.js';

	interface Props {
		form;
		item: Item;
		value: number;
	}

	let { form, item, value = $bindable() }: Props = $props();

	let sliderValue = $state([value]);

	$effect(() => {
		value = sliderValue[0];
	});
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
				<Slider
					min={item.scale_min}
					max={item.scale_max}
					step={0.1}
					bind:value={sliderValue}
					{...attrs}
				/>
			</Card.Content>
		</Form.Control>
		<Form.FieldErrors />
	</Form.Field>
</Card.Root>
