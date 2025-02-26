import type { LayoutServerLoad } from './$types';
import type { Project } from '$lib/project.svelte';
import { error, redirect } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ parent, params }) => {
	const { projects } = await parent();
	const projectId = params.projectId;

	if (!projectId) {
		throw error(400, 'Project ID is required');
	}

	const currentProject = projects.find((project: Project) => project.id === Number(projectId));

	if (!currentProject) {
		throw redirect(303, '/projects');
	}

	return {
		projects,
		currentProject
	};
};
