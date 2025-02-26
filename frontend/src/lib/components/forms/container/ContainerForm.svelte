<script lang="ts">
	import * as Card from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button';
	import * as Form from '$lib/components/ui/form/index.js';
	import { Input } from '$lib/components/ui/input';
	import {
		type ContainerFormSchema,
		containerFormSchema
	} from '$lib/components/forms/container/schema.js';
	import { type SuperValidated, superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { dev } from '$app/environment';
	import SuperDebug from 'sveltekit-superforms';

	interface Props {
		data: SuperValidated<ContainerFormSchema>;
		action: string;
	}

	let { data, action }: Props = $props();
	let form = superForm(data, {
		validators: zodClient(containerFormSchema),
		dataType: 'json',
		resetForm: action.includes('create')
	});
	let { form: formData, enhance, errors } = $derived(form);

	function addPort() {
		$formData.ports = [...($formData.ports || []), { internal_port: 0 }];
	}

	function removePort(index: number) {
		$formData.ports = $formData.ports.filter((_, i) => i !== index);
	}
</script>

<form method="POST" use:enhance class="w-full" {action}>
	<Card.Root class="w-full">
		<Card.Header>
			<Card.Title>Container</Card.Title>
			<Card.Description>Configure your container here.</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4 w-full">
			<Form.Field {form} name="name">
				<Form.Control let:attrs>
					<Form.Label>Container Name</Form.Label>
					<Input bind:value={$formData.name} {...attrs} placeholder="Simulation Container" />
				</Form.Control>
				<Form.Description
					>The name of your container. Only for internal tracking purposes.</Form.Description
				>
				<Form.FieldErrors />
			</Form.Field>
			<Form.Field {form} name="dockerfile">
				<Form.Control let:attrs>
					<Form.Label>Dockerfile</Form.Label>
					<Input bind:value={$formData.dockerfile} {...attrs} placeholder="./Dockerfile" />
				</Form.Control>
				<Form.Description
					>Path to the location of the Dockerfile relative to the root of your repo.</Form.Description
				>
				<Form.FieldErrors />
			</Form.Field>
			<Form.Field {form} name="ports">
				<Form.Control>
					<Form.Label>Ports</Form.Label>
					<Form.Description
						>Map container ports to host ports. Internal port is the port inside the container,
						external port is the port on your host machine.</Form.Description
					>
					{#if $formData.ports && $formData.ports.length > 0}
						{#each $formData.ports as port, index}
							<div class="flex items-end space-x-2 mt-4">
								<div class="flex-1">
									<Form.Field {form} name={`ports.${index}.internal_port`}>
										<Form.Control let:attrs>
											<Form.Label>Internal Port (Container)</Form.Label>
											<Input
												type="number"
												bind:value={$formData.ports[index].internal_port}
												{...attrs}
												placeholder="e.g., 8080"
											/>
										</Form.Control>
									</Form.Field>
								</div>
								<div class="flex-1">
									<Form.Field {form} name={`ports.${index}.external_port`}>
										<Form.Control let:attrs>
											<Form.Label>External Port (Host)</Form.Label>
											<Input
												type="number"
												bind:value={$formData.ports[index].external_port}
												{...attrs}
												placeholder="e.g., 80"
											/>
										</Form.Control>
									</Form.Field>
								</div>
								<Button type="button" variant="destructive" on:click={() => removePort(index)}
									>Remove</Button
								>
							</div>
						{/each}
					{/if}
					<Button type="button" class="mt-4" on:click={addPort}>Add Port</Button>
				</Form.Control>
				<Form.FieldErrors />
			</Form.Field>
		</Card.Content>
		<Card.Footer class="flex justify-end">
			<Form.Button>Submit</Form.Button>
		</Card.Footer>
	</Card.Root>
</form>
<!-- <SuperDebug data={$formData} display={dev} /> -->