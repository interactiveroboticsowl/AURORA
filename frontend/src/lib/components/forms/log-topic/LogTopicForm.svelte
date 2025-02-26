<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Form from '$lib/components/ui/form/index.js';
	import { Input } from '$lib/components/ui/input';

	import { type SuperValidated, superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { dev } from '$app/environment';
	import SuperDebug from 'sveltekit-superforms';
	import { logTopicFormSchema, type LogTopicFormSchema } from './schema';

	interface Props {
		data: SuperValidated<LogTopicFormSchema>;
	}

	let { data }: Props = $props();
	// let formData = $derived(data)
	let form = superForm(data, {
		validators: zodClient(logTopicFormSchema),
		dataType: 'json'
	});
	let { form: formData, enhance } = $derived(form);

	function addTopic(topicName: string) {
		$formData.topics = [...$formData.topics, topicName];
	}

	function removeTopic(index: number) {
		$formData.topics = $formData.topics.filter((_, i) => i !== index);
	}
</script>

<form method="POST" use:enhance class="w-full pl-4 pr-4" action="?/topics">
	<Form.Field {form} name="topics">
		<Form.Control>			
			<Form.Description>List the ros topics to record. If none are specified, all topics will be recorded.</Form.Description>
			{#each $formData.topics as topic, index}
				<div class="flex justify-between">
					<Form.Field {form} name={`topics.${index}`}>
						<Form.Control let:attrs>						
							<Input
								type="text"								
								bind:value={$formData.topics[index]}
								{...attrs}
								placeholder="e.g., /tf"
							/>
						</Form.Control>
					</Form.Field>
					<Button type="button" variant="destructive" on:click={() => removeTopic(index)}
						>Remove</Button
					>
				</div>
			{/each}
		</Form.Control>
		<Form.FieldErrors />
	</Form.Field>
	<div class="flex gap-2 mt-4">
		<Button type="button" variant="outline" on:click={() => addTopic('name')}>Add Topic</Button>
		<Form.Button type="submit">Save</Form.Button>
	</div>
</form>
