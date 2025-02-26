<script lang="ts">
	import * as Card from '$lib/components/ui/card/index.js';
	import type { Item } from '$lib/components/survey/schemaGenerator';
	import { onMount } from 'svelte';

	interface Props {
		item: Item;
	}

	let { item }: Props = $props();
	let hydrated = $state(false);

	onMount(() => {
		hydrated = true;
	});
</script>

<Card.Root class="mx-2">
	<Card.Header>
		<Card.Title>{item.title}</Card.Title>
		{#if item.prompt}
			<Card.Description
				>{#key hydrated}{@html item.prompt}{/key}</Card.Description
			>
		{/if}
	</Card.Header>
	<Card.Content>
		<p>
			{#key hydrated}
				{@html item.text_content}{/key}
		</p>
	</Card.Content>
</Card.Root>
