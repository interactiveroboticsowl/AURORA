<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import { type ProjectSchema, projectSchema } from '$lib/components/forms/project/schema';
	import { type SuperValidated, superForm, type Infer } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { Input } from '$lib/components/ui/input';

	interface Props {
		data: SuperValidated<Infer<ProjectSchema>>;
	}

	let { data }: Props = $props();
	let form = superForm(data, {
		validators: zodClient(projectSchema)
	});

	const { form: formData, enhance } = form;
</script>

<form method="POST" use:enhance>
	<Form.Field {form} name="name">
		<Form.Control let:attrs>
			<Form.Label>Name</Form.Label>
			<Input bind:value={$formData.name} {...attrs} placeholder="Project Name" />
		</Form.Control>
		<Form.Description>Please enter the name of the new project</Form.Description>
		<Form.FieldErrors />
	</Form.Field>
	<Form.Button>Submit</Form.Button>
</form>
