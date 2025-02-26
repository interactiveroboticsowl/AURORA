import { pageSchema } from '$lib/components/forms/survey/schema';
import { type Actions } from '@sveltejs/kit';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config';
import { redirect } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ parent }) => {
	const { survey } = await parent();

	if (!survey) {
		return redirect(404, `/projects/${survey.id}/survey`);
	}

	const form = await superValidate({ survey_id: survey.id, order: 0 }, zod(pageSchema)); // Set default order here

	return { form };
};

export const actions: Actions = {
	default: async (event) => {
		const form = await superValidate(event, zod(pageSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		if (!form.data.order) {
			form.data.order = 0;
		}

		const response = await event.fetch(
			`${API_BASE_URL}/api/surveys/${form.data.survey_id}/pages/`,
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
			return fail(response.status, {
				form,
				error: errorData.message || 'Error occurred'
			});
		}

		const createdData = await response.json();

		return redirect(
			`/projects/${form.data.survey_id}/survey/pages/${createdData.id}`,
			{ message: 'Page created', type: 'success' },
			event.cookies
		);
	}
};
