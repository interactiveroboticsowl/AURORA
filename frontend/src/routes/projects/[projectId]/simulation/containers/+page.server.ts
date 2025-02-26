import { error, fail } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { containerFormSchema } from '$lib/components/forms/container/schema';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { API_BASE_URL } from '$lib/config';
import { setFlash } from 'sveltekit-flash-message/server';
import { redirect } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ parent }) => {
	const { containers } = await parent()
	const containerForm = await superValidate(zod(containerFormSchema));

	return {
		containers,
		containerForm
	};
};

export const actions: Actions = {
	create: async ({ request, fetch, params, cookies }) => {
		const form = await superValidate(request, zod(containerFormSchema));
		if (!form.valid) {
			return fail(400, { form });
		}
		if (!params.projectId) {
			return fail(404, { form, error: 'Project ID is required' });
		}

		const response = await fetch(
			`${API_BASE_URL}/api/projects/${params.projectId}/application/containers/`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(form.data)
			}
		);
		if (!response.ok) {
			const errorData = await response.json();
			setFlash({ message: 'Failed to create container', type: 'error' }, cookies);
			return fail(response.status, { form, error: errorData.message || 'Error occurred' });
		}

		const createdData = await response.json();

		// setFlash({ message: 'Container created', type: 'success' }, cookies);

		return redirect(
			`/projects/${params.projectId}/simulation/containers/${createdData.id}`,
			{ message: 'Container created', type: 'success' },
			cookies
		);
	}
};
