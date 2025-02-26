import { redirect } from 'sveltekit-flash-message/server';
import type { PageServerLoad, Actions } from './$types';
import { zod } from 'sveltekit-superforms/adapters';
import { containerFormSchema } from '$lib/components/forms/container/schema';
import { superValidate } from 'sveltekit-superforms';
import { API_BASE_URL } from '$lib/config';
import { setFlash } from 'sveltekit-flash-message/server';
import { fail } from 'sveltekit-superforms';

export const load: PageServerLoad = async ({ params, parent, cookies }) => {
	const { containers } = await parent();
	const { projectId, containerId } = params;

	if (!projectId) {
		return redirect('/projects', { message: 'Please select a project', type: 'error' }, cookies);
	}

	if (!containerId) {
		return redirect(
			`/projects/${projectId}/application/containers`,
			{ message: 'Please select a container', type: 'error' },
			cookies
		);
	}	

	const container = containers.find((c) => c.id == containerId);

	const containerForm = await superValidate(container, zod(containerFormSchema));

	return { containerForm };
};

export const actions: Actions = {
	update: async ({ request, fetch, params, cookies }) => {
		const form = await superValidate(request, zod(containerFormSchema));
		if (!form.valid) {
			return fail(400, { form });
		}
		if (!params.projectId) {
			return fail(404, { form, error: 'Project ID is required' });
		}

		const method = form.data.id ? 'PUT' : 'POST';
		const url = form.data.id
			? `${API_BASE_URL}/api/projects/${params.projectId}/application/containers/${form.data.id}`
			: `${API_BASE_URL}/api/projects/${params.projectId}/application/containers/`;

		const response = await fetch(url, {
			method,
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(form.data)
		});

		if (!response.ok) {
			const errorData = await response.json();
			return fail(response.status, {
				form,
				error: errorData.message || 'Error occurred'
			});
		}
		const updatedData = await response.json();

		// Update the form with the new data
		const updatedForm = await superValidate(updatedData, zod(containerFormSchema));

		setFlash({ message: 'Container updated', type: 'success' }, cookies);

		return {
			form: updatedForm
		};
	},
	delete: async ({ params, fetch, request, cookies }) => {
		const data = await request.formData();		
		if (!params.projectId) {
			return fail(404, { error: 'Project ID is required' });
		}
		const response = await fetch(
			`${API_BASE_URL}/api/projects/${params.projectId}/application/containers/${data.get('id')}`,
			{
				method: 'DELETE'
			}
		);
		if (!response.ok) {
			const errorData = await response.json();
			setFlash({ message: 'Failed to delete container', type: 'error' }, cookies);
			return fail(response.status, { error: errorData.message || 'Error occurred' });
		}
		redirect(
			`/projects/${params.projectId}/simulation/containers`,
			{ message: 'Container deleted', type: 'success' },
			cookies
		);
	}
};
