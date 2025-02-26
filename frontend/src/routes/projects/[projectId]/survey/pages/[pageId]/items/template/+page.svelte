<script lang="ts">
	import ItemTemplateForm from '$lib/components/forms/item-template/ItemTemplateForm.svelte';
	import { superValidate } from 'sveltekit-superforms';
	import { zod } from 'sveltekit-superforms/adapters';
	import { itemTemplateSchema } from '$lib/components/forms/item-template/schema';

	const data = superValidate(zod(itemTemplateSchema));
</script>

<div class="px-2 pt-2 h-screen">
	<ItemTemplateForm {data} />
</div>
