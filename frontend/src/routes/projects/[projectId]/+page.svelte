<script lang="ts">
	import * as Resizable from '$lib/components/ui/resizable/index.js';
	import { Separator } from '$lib/components/ui/separator';
	import PublicationCard from '$lib/components/publication/PublicationCard.svelte';
	import type { PageData } from './$types';

	let { data } = $props<{ data: PageData }>();
	let { publications, publicationFormData } = $derived(data);
</script>

<Resizable.Pane minSize={30}>
	<div class="flex items-center px-4 py-2 h-[52px]">
		<h1 class="text-xl font-bold">Dashboard</h1>
	</div>
	<Separator />
	<div class="flex justify-center items-start h-full w-full mt-12">
		<PublicationCard {publications} {publicationFormData} />
	</div>
</Resizable.Pane>