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
	<!-- svelte-ignore a11y_media_has_caption -->
	<video controls>
		<source src={item.video_url} type="video/mp4" />
		Your browser does not support the video tag.
	</video>
	<Card.Content></Card.Content>
</Card.Root>
