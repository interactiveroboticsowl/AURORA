<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { type PageSchema, pageSchema } from '$lib/components/forms/survey/schema';
	import { type SuperValidated, superForm, type Infer } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { Input } from '$lib/components/ui/input';
	import { Checkbox } from '$lib/components/ui/checkbox';

	import { dev } from '$app/environment';
	import SuperDebug from 'sveltekit-superforms';
	interface Props {
		data: SuperValidated<PageSchema>;
	}

	let { data }: Props = $props();
	let form = superForm(data, {
		validators: zodClient(pageSchema),
		dataType: 'json',
		resetForm: false
	});

	const { form: formData, enhance } = form;
</script>

<form method="POST" use:enhance>
	<Form.Field {form} name="name">
		<Form.Control let:attrs>
			<Form.Label>Name</Form.Label>
			<Input bind:value={$formData.name} {...attrs} placeholder="Page Name" />
		</Form.Control>
		<Form.Description>Please enter the name of the page</Form.Description>
		<Form.FieldErrors />
	</Form.Field>
	<Form.Field {form} name="description">
		<Form.Control let:attrs>
			<Form.Label>Description</Form.Label>
			<Input bind:value={$formData.description} {...attrs} placeholder="Page Description" />
		</Form.Control>
		<Form.Description>Please enter the description of the page</Form.Description>
		<Form.FieldErrors />
	</Form.Field>
	<Form.Field {form} name="application_enabled">
		<Form.Control let:attrs>
			<Form.Label>Application Enabled</Form.Label>
			<Checkbox {...attrs} bind:checked={$formData.application_enabled} />
		</Form.Control>
		<Form.Description>Is the application enabled for this page?</Form.Description>
	</Form.Field>

	<Form.Field {form} name="back_button_disabled">
		<Form.Control let:attrs>
			<Form.Label>Back button disabled</Form.Label>
			<Checkbox {...attrs} bind:checked={$formData.back_button_disabled} />
		</Form.Control>
		<Form.Description>Is the back button disabled for this page?</Form.Description>
	</Form.Field>
	<Form.Button>Submit</Form.Button>
</form>

<!-- <SuperDebug data={$formData} display={dev} /> -->
