<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { type SurveySchema, surveySchema } from '$lib/components/forms/survey/schema';
	import { type SuperValidated, superForm, type Infer } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { Input } from '$lib/components/ui/input';

	import { dev } from '$app/environment';
	import SuperDebug from 'sveltekit-superforms';
	interface Props {
		data: SuperValidated<SurveySchema>;
	}

	let { data }: Props = $props();
	let form = superForm(data, {
		validators: zodClient(surveySchema),
		dataType: 'json',
		resetForm: false
	});

	const { form: formData, enhance } = form;
</script>

<form method="POST" use:enhance>
	<Form.Field {form} name="title">
		<Form.Control let:attrs>
			<Form.Label>Title</Form.Label>
			<Input bind:value={$formData.title} {...attrs} placeholder="Survey Title" />
		</Form.Control>
		<Form.Description>Please enter the title of the new survey</Form.Description>
		<Form.FieldErrors />
	</Form.Field>
	<Form.Field {form} name="description">
		<Form.Control let:attrs>
			<Form.Label>Description</Form.Label>
			<Input bind:value={$formData.description} {...attrs} placeholder="Description" />
		</Form.Control>
		<Form.Description>Please enter a description for the survey</Form.Description>
		<Form.FieldErrors />
	</Form.Field>
	<Form.Button>Submit</Form.Button>
</form>

<!-- <SuperDebug data={$formData} display={dev} /> -->
