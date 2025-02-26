import type { LayoutServerLoad } from './$types';
import type { Project } from '$lib/project.svelte';
import { API_BASE_URL } from '$lib/config';
import { error } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
	const layoutCookie = cookies.get('PaneForge:layout');
	let layout: number[] | undefined;

	if (layoutCookie) layout = JSON.parse(layoutCookie);

	const response = await fetch(`${API_BASE_URL}/api/projects/`);
	if (!response.ok) {
		return error(500, 'Failed to fetch projects');
	}
	const projects = await response.json();

	return {
		projects: projects,
		layout: layout
	};
};
