import { error, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { pageSchema, surveySchema } from '$lib/components/forms/survey/schema';
import { setFlash } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const projectId = params.projectId;

	if (!projectId) {
		return error(404, 'Project ID is required');
	}

	const { survey } = await parent();

	if (survey) {
		const form = await superValidate(survey, zod(surveySchema));
		return { survey, form };
	}

	const form = await superValidate({ project_id: Number(params.projectId) }, zod(surveySchema));

	return { form };
};

export const actions: Actions = {
	default: async (event) => {
		const form = await superValidate(event, zod(surveySchema));
		if (!form.valid) {
			return fail(400, {
				form
			});
		}

		const url = form.data.id
			? `${API_BASE_URL}/api/surveys/${form.data.id}`
			: `${API_BASE_URL}/api/surveys/`;

		const response = await event.fetch(url, {
			method: form.data.id ? 'PUT' : 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(form.data)
		});

		if (!response.ok) {
			const errorData = await response.json();
			return fail(response.status, {
				form,
				error: errorData.message || 'Error occoured'
			});
		}
		if (!form.data.id) {
			setFlash({ message: 'Survey created', type: 'success' }, event.cookies);
		} else {
			setFlash({ message: 'Survey updated', type: 'success' }, event.cookies);
		}
		return {
			form
		};
	}
};
