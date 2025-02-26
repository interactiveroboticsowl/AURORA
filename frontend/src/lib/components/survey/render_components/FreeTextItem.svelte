<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import type { Item } from '$lib/components/survey/schemaGenerator';
	import { Textarea } from '$lib/components/ui/textarea';

	import * as Card from '$lib/components/ui/card/index.js';

	interface Props {
		form;
		item: Item;
		value: string;
	}

	let { form, item, value = $bindable() }: Props = $props();
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
				<Textarea bind:value {...attrs} />
			</Card.Content>
		</Form.Control>
		<Form.FieldErrors />
	</Form.Field>
</Card.Root>
