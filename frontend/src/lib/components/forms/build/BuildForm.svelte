<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import * as Select from '$lib/components/ui/select/index'
	import { type BuildSchema, buildSchema } from '$lib/components/forms/build/schema';
	import SuperDebug, { type SuperValidated, superForm, type Infer } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import type { Selected } from 'bits-ui';

	interface Props {
		data: SuperValidated<Infer<BuildSchema>>;
	}

	let { data }: Props = $props();
	let form = superForm(data, {
		validators: zodClient(buildSchema)
	});

	const rosVersions: { [v: string]: string } = { "1": "ROS 1 (ros-one)", "2": "ROS 2 (humble)" }

	const { form: formData, enhance } = form;
	let selectedVersion: Selected<string> = $state({ value: $formData.ros_version, label: rosVersions[$formData.ros_version] })

	console.log(selectedVersion)

	const selectNewVersion = (v: { value: string } | undefined) => {
		if (!v)
			return;

		$formData.ros_version =  v.value		
	}
</script>

<form method="POST" class="flex" action="?/build" use:enhance>
		<Form.Field {form} name="ros_version" class="w-[200px]">
			<Form.Control let:attrs>
				<Select.Root selected={selectedVersion} onSelectedChange={selectNewVersion}>
					<Select.Trigger {...attrs} >
						<Select.Value placeholder="ROS Version" />
					</Select.Trigger>
					<Select.Content>
						<Select.Item value="1">ROS 1 (ros-one)</Select.Item>
						<Select.Item value="2">ROS 2 (humble)</Select.Item>
					</Select.Content>
				</Select.Root>
				<input hidden bind:value={$formData.ros_version} name={attrs.name} />
			</Form.Control>
		</Form.Field>
		<Form.Button class="ml-4">Build</Form.Button>		
</form>
