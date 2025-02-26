<script lang="ts">
	import type { Item } from '$lib/components/survey/schemaGenerator';
	import * as Card from '$lib/components/ui/card/index.js';

	interface Props {
		item: Item;
	}

	let { item }: Props = $props();
</script>

<Card.Root class="mx-2">
	<Card.Header>
		<Card.Title>{item.title}</Card.Title>
		{#if item.prompt}
			<Card.Description>{item.prompt}</Card.Description>
		{/if}
	</Card.Header>
	<img src={item.image_url} alt={item.title} />
	<Card.Content></Card.Content>
</Card.Root>
