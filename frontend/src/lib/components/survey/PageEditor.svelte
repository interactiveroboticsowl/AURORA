<script lang="ts">
	import { Separator } from '$lib/components/ui/separator';
	import PageForm from '$lib/components/forms/survey/PageForm.svelte';
	import { type SuperValidated } from 'sveltekit-superforms/client';
	import { type PageSchema } from '$lib/components/forms/survey/schema';

	interface Props {
		data: SuperValidated<PageSchema>;
	}

	let { data }: Props = $props();
</script>

<div class="flex h-[52px] items-center text-xl pl-4">Edit Page</div>
<Separator />
<PageForm {data} />
