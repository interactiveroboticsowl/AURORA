<script lang="ts">
	import SurveyPreviewRenderer from '$lib/components/survey/SurveyPreviewRenderer.svelte';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import { Separator } from '$lib/components/ui/separator';

	let { data } = $props();
	let { pages } = data;
	const participant_id = 1;
</script>

<div class="flex h-[52px] items-center">
	<h1 class="text-2xl font-bold pl-2">Preview</h1>
</div>
<Separator />
<div class="flex flex-col h-[calc(100vh-54px)]">
	<ScrollArea class="flex-grow p-2">
		<SurveyPreviewRenderer {pages} {participant_id} preview={true} />
	</ScrollArea>
</div>
