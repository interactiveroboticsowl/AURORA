import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { Auth, raw } from '@auth/core';
import { config } from '../../../auth';
import client from '$lib/api/index.js';

export const load: LayoutServerLoad = async ({ params, fetch, locals, cookies, url }) => {
	const uuid = params.publicationUUID;
	const session = await locals.auth();
	let participant_id = Number(session?.user?.id);

	const external_id = url.searchParams.get('participant_id');
	const external_survey_id = url.searchParams.get('survey_id');
	const external_session_id = url.searchParams.get('session_id');

	if (!uuid) {
		return error(404, 'UUID is required');
	}

	const publication = await client.GET('/api/publications/uuid/{link_uuid}', {
		params: { path: { link_uuid: uuid } },
		fetch
	});

	if (publication.error) {
		return error(403);
	}

	if (!session?.user) {
		const participant = await client.POST('/api/participants/', {
			body: {
				external_id,
				external_survey_id,
				external_session_id
			},
			fetch
		});

		if (participant.error) {
			return error(500, 'Failed to create participant');
		}

		const req = new Request(`${url.protocol + url.host}/auth/callback/end-user-credentials`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
			body: new URLSearchParams({ id: String(participant.data.id) })
		});
		const res = await Auth(req, { ...config, raw });
		for (const c of res?.cookies ?? []) {
			cookies.set(c.name, c.value, { path: '/', ...c.options });
		}
		participant_id = participant.data.id;
	}

	const routes = await client.GET('/api/publications/{publication_id}/deploy/{participant_id}', {
		params: { path: { publication_id: publication.data.id, participant_id } },
		fetch
	});

	if (routes.error) {
		return error(500, 'Failed to deploy publication');
	}

	if (publication.data.application_only) {
		return {
			routes: routes.data
		};
	}

	const survey = await client.GET('/api/projects/{project_id}/survey', {
		params: { path: { project_id: publication.data.project_id } },
		fetch
	});

	if (survey.error) {
		return error(500, 'Failed to get survey');
	}

	return {
		routes: routes.data,
		survey: survey.data
	};
};
