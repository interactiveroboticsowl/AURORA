import { API_BASE_URL } from '$lib/config';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params, parent }) => {
	const { survey } = await parent();

	if (!survey) {
		return {
			status: 404,
			error: 'Survey not found'
		};
	}

	const response = await fetch(`${API_BASE_URL}/api/surveys/${survey.id}/pages/`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json'
		}
	});

	if (!response.ok) {
		const errorData = await response.json();
		return {
			error: errorData.message || 'Error occurred'
		};
	}

	const data = await response.json();
	const pages = data;

	return { pages };
};
