<script lang="ts">
	import { Separator } from '$lib/components/ui/separator';
	import ItemForm from '$lib/components/forms/survey/ItemForm.svelte';
	import type { PageData } from './$types';

	let { data } = $props<{ data: PageData }>();
</script>

<div class="flex h-[52px] items-center">
	<h1 class="text-2xl font-bold pl-2">Create Item</h1>
</div>

<div class="p-2">
	<ItemForm data={data.form} />
</div>
