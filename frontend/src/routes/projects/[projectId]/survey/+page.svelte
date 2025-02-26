<script lang="ts">
	import { Separator } from '$lib/components/ui/separator';
	import type { PageData } from './$types';
	import SurveyForm from '$lib/components/forms/survey/SurveyForm.svelte';

	let { data } = $props<{ data: PageData }>();
</script>

<div class="flex h-[52px] items-center">
	<h1 class="text-2xl font-bold pl-2">{data.survey ? 'Edit Survey' : 'Add Survey'}</h1>
</div>
<Separator />
<div class="p-2">
	<SurveyForm data={data.form} />
</div>
