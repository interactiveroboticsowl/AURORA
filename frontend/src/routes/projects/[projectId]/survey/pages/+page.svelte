<script lang="ts">
	import { Separator } from '$lib/components/ui/separator';
	import PageForm from '../../../../../lib/components/forms/survey/PageForm.svelte';
	import type { PageData } from './$types';

	let { data } = $props<{ data: PageData }>();
</script>

<div class="flex h-[52px] items-center">
	<h1 class="text-2xl font-bold pl-2">Add Page</h1>
</div>
<Separator />
<div class="p-2">
	<PageForm data={data.form} />
</div>
