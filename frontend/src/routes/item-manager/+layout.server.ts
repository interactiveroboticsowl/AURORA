import type { LayoutServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config';
import { error } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ fetch }) => {
	const response = await fetch(`${API_BASE_URL}/api/projects/`);
	if (!response.ok) {
		throw error(500, 'Failed to fetch projects');
	}
	const projects = await response.json();

	return {
		projects
	};
};
