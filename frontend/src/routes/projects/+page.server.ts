import type { PageServerLoad } from './$types.js';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { projectSchema } from '$lib/components/forms/project/schema';
import { fail, type Actions } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config';
import { redirect } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ parent }) => {
	const { projects } = await parent();
	return {
		form: await superValidate(zod(projectSchema)),
		projects
	};
};

export const actions: Actions = {
	default: async (event) => {
		const form = await superValidate(event, zod(projectSchema));
		if (!form.valid) {
			return fail(400, {
				form
			});
		}

		const response = await event.fetch(`${API_BASE_URL}/api/projects/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(form.data)
		});

		if (!response.ok) {
			const errorData = await response.json();
			return fail(response.status, {
				form,
				error: errorData.message || 'Error occured'
			});
		}

		const created_project = await response.json();

		return redirect(
			`/projects/${created_project.id}`,
			{ message: 'Project created', type: 'success' },
			event.cookies
		);
	}
};
