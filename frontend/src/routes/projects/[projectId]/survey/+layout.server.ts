import { error, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config';
import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { pageSchema, surveySchema } from '$lib/components/forms/survey/schema';

export const load: PageServerLoad = async ({ params, fetch, depends }) => {
	depends('project:survey');
	const projectId = params.projectId;

	if (!projectId) {
		return error(404, 'Project ID is required');
	}

	const response = await fetch(`${API_BASE_URL}/api/projects/${params.projectId}/survey`);

	if (response.ok) {
		const survey = await response.json();

		return { survey };
	}

	if (response.status != 404) {
		return error(500, 'Failed to fetch survey');
	}

	const form = await superValidate(zod(surveySchema));

	return { form };
};
