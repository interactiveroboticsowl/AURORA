import type { PageServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms/server';
import { zod } from 'sveltekit-superforms/adapters';
import { publicationSchema } from '$lib/components/publication/schema';
import type { Actions } from '@sveltejs/kit';
import { fail } from '@sveltejs/kit';
import { API_BASE_URL } from '$lib/config';
import { setFlash } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ params }) => {
	const publicationFormData = await superValidate(
		{ project_id: Number(params.projectId) },
		zod(publicationSchema)
	);

	const res = await fetch(`${API_BASE_URL}/api/projects/${params.projectId}/publications`);
	if (!res.ok) {
		return fail(res.status);
	}

	const publications = await res.json();
	if (!publications) {
		return fail(500, 'Failed to fetch publications');
	}

	return {
		publicationFormData,
		publications: publications
	};
};

export const actions: Actions = {
	createPublication: async (event) => {
		const form = await superValidate(event, zod(publicationSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await event.fetch(`${API_BASE_URL}/api/publications/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(form.data)
		});

		if (!response.ok) {
			const errorData = await response.json();
			console.log(errorData);
			return fail(response.status, {
				form,
				error: errorData.message || 'Error occurred'
			});
		}

		setFlash({ message: 'Publication created', type: 'success' }, event.cookies);

		return {
			form
		};
	}
};
