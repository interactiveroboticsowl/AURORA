import type { LayoutServerLoad } from './$types';
import { superValidate } from 'sveltekit-superforms/server';
import { gitRepoSchema } from '$lib/components/repo/schema';
import { zod } from 'sveltekit-superforms/adapters';
import { API_BASE_URL } from '$lib/config';
import { redirect } from 'sveltekit-flash-message/server';
import { containerFormSchema } from '$lib/components/forms/container/schema';
import { buildSchema } from '$lib/components/forms/build/schema';
import { logTopicFormSchema } from '$lib/components/forms/log-topic/schema';

// TODO: refactor, cleanup
export const load: LayoutServerLoad = async ({ params, fetch, cookies }) => {
	const projectId = params.projectId;

	const repoFormData = await superValidate(zod(gitRepoSchema));	
	const buildFormData = await superValidate(zod(buildSchema))
	const topicsFormData = await superValidate(zod(logTopicFormSchema))

	const applictionResponse = await fetch(`${API_BASE_URL}/api/projects/${projectId}/application/`);
	if (!applictionResponse.ok) {
		return redirect(
			`/projects/${projectId}`,
			{
				message: 'Failed to fetch application',
				type: 'error'
			},
			cookies
		);
	}
	const containersResponse = await fetch(`${API_BASE_URL}/api/projects/${projectId}/application/containers`);

	if (!containersResponse.ok) {
		return redirect('/projects', { message: 'Failed to fetch containers', type: 'error' }, cookies);
	}

	const applicationData = await applictionResponse.json();
	const containers = await containersResponse.json();

	buildFormData.data.ros_version = applicationData.ros_version

	const repo_response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/repo`);

	// TODO: why should repo_response be not ok?
	if (!repo_response.ok) {
		return {			
			repoFormData,
			applicationData,
			buildFormData,
			topicsFormData,
			containers
		};
	}

	const repoData = await repo_response.json();
	repoFormData.data = repoData;	

	return {		
		repoFormData,
		applicationData,
		buildFormData,
		topicsFormData,
		containers
	};
};