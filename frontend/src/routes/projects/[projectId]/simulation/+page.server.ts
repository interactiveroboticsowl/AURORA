
import { fail, type Actions } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms/server';
import { setFlash } from 'sveltekit-flash-message/server';
import { API_BASE_URL } from '$lib/config';
import { gitRepoSchema } from '$lib/components/repo/schema';
import { zod } from 'sveltekit-superforms/adapters';
import { buildSchema } from '$lib/components/forms/build/schema';

export const actions: Actions = {
	repo: async (event) => {
		const form = await superValidate(event, zod(gitRepoSchema));		
		form.data.application_id = Number(event.params.projectId);
		if (!form.valid) {
			return fail(400, {
				form
			});
		}

		const response = await event.fetch(
			`${API_BASE_URL}/api/projects/${event.params.projectId}/repo`,
			{
				method: form.data.id ? 'PUT' : 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(form.data)
			}
		);

		if (!response.ok) {
			const errorData = await response.json();
			return fail(response.status, {
				form,
				error: errorData.message || 'Error occoured'
			});
		}
		
		if (form.data.id) {
			setFlash({ message: 'Repository updated', type: 'success' }, event.cookies);
		} else {
			setFlash({ message: 'Repository created', type: 'success' }, event.cookies);
		}

		return {
			form
		};
	},
	build: async ({ request, fetch, params }) => {
		const form = await superValidate(request, zod(buildSchema));
		if (!form.valid) {
			return fail(400, { form });
		}
		const projectId = params.projectId;

		if (!projectId) {
			return fail(400, { form, error: 'Project ID is required'});
		}

		const a = await fetch(`${API_BASE_URL}/api/projects/${projectId}/application`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (!a.ok) {
			return fail(500, { form, error: 'Failed to fetch application' });
		}

		const application = await a.json();

		const prev_build_version = application.build_version;

		const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/application`, {
			method: 'PATCH',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ ros_version: form.data.ros_version, build_version: prev_build_version + 1 })
		});

		if (!response.ok) {
			return fail(500, { form, error: 'Failed to build application'});
		}

		return {
			form,
			build_version: prev_build_version + 1
		};
	},	
};
