<script lang="ts">
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Form from '$lib/components/ui/form/index.js';
	import * as flashModule from "sveltekit-flash-message/client"
	import { Input } from '$lib/components/ui/input';
	import { type GitRepoSchema, gitRepoSchema } from '$lib/components/repo/schema';
	import { type SuperValidated, superForm, type Infer } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import Separator from '../ui/separator/separator.svelte';

	interface Props {
		data: SuperValidated<Infer<GitRepoSchema>>;
	}

	let { data }: Props = $props();
	const form = superForm(data, {
		validators: zodClient(gitRepoSchema),
		syncFlashMessage: true,
		resetForm: false
	});
	const { form: formData, enhance } = form;
</script>

<form method="POST" use:enhance class="w-full max-w-md mx-auto" action="?/repo">
	<input type="hidden" name="id" bind:value={$formData.id} />
	<div class="w-full">
		<div class="flex h-[52px] items-center text-xl px-4">Repository</div>
		<Separator />
		<div class="px-4">
			<div class="pb-4 pt-4 text-sm text-gray-600">Connect your repository to get started.</div>				
			<Form.Field {form} name="git_url">
				<Form.Control let:attrs>
					<Form.Label>Repository URL</Form.Label>
					<Input
						bind:value={$formData.git_url}
						{...attrs}
						placeholder="https://github.com/username/repo"
					/>
				</Form.Control>
				<Form.Description>Enter the URL of your repository.</Form.Description>
				<Form.FieldErrors />
			</Form.Field>
			<Form.Field {form} name="access_token">
				<Form.Control let:attrs>
					<Form.Label>Authentication Token</Form.Label>
					<Input
						bind:value={$formData.access_token}
						{...attrs}
						type="password"
						placeholder="Enter your token"
					/>
				</Form.Control>
				<Form.Description>Enter your authentication token.</Form.Description>
				<Form.FieldErrors />
			</Form.Field>
			<Form.Field {form} name="git_branch">
				<Form.Control let:attrs>
					<Form.Label>Branch</Form.Label>
					<Input bind:value={$formData.git_branch} {...attrs} placeholder="main" />
				</Form.Control>
				<Form.Description>Enter the branch name (e.g., main, master, develop).</Form.Description>
				<Form.FieldErrors />
			</Form.Field>
		</div>
		<div class="flex justify-end pr-4">
			<Form.Button>Submit</Form.Button>
		</div>
	</div>
</form>
