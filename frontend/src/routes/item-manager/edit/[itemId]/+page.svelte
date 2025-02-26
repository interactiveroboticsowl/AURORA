<script lang="ts">
	import { Separator } from '$lib/components/ui/separator';
	import ItemForm from '$lib/components/forms/survey/ItemForm.svelte';
	import type { PageData } from './$types';

	let { data } = $props<{ data: PageData }>();
</script>

<div class="flex h-[52px] items-center">
	<h1 class="text-2xl font-bold pl-2">Edit Item</h1>

</div>
<Separator />
<div class="p-2">
	<div class="text-red-600">
		<span class="font-semibold block">Warning:</span>
		Editing a survey item will update it in all surveys where it has been added, including those that are currently published. Changes made will be reflected immediately and may impact the responses of ongoing surveys.
	</div>
	<ItemForm data={data.form} />
</div>
