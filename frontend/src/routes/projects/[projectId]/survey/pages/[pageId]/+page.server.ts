import { pageSchema } from '$lib/components/forms/survey/schema';
import { redirect, type Actions } from '@sveltejs/kit';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config';
import { setFlash } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const pageId = params.pageId;

	if (!pageId) {
		return redirect(404, `/projects/${params.projectId}/survey`);
	}

	const response = await fetch(`${API_BASE_URL}/api/pages/${pageId}`);

	if (!response.ok) {
		return redirect(404, `/projects/${params.projectId}/survey`);
	}

	const pageData = await response.json();

	if (!pageData) {
		return redirect(303, `/projects/${params.projectId}/survey`);
	}

	const form = await superValidate(pageData, zod(pageSchema));

	return { form };
};

export const actions: Actions = {
	default: async (event) => {
		const form = await superValidate(event, zod(pageSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await event.fetch(`${API_BASE_URL}/api/pages/${form.data.id}`, {
			method: 'PUT',
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

		setFlash({ message: 'Page updated', type: 'success' }, event.cookies);

		return {
			form
		};
	}
};
