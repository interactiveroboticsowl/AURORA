import { generateSchemaForPage } from '$lib/components/survey/schemaGenerator.js';
import { error, redirect, type Actions, fail } from '@sveltejs/kit';
import type { PageServerLoad } from './$types.js';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { API_BASE_URL } from '$lib/config';

export const load: PageServerLoad = async ({
	params,
	fetch,
	locals,
	cookies,
	url,
	parent,
	depends
}) => {
	const { pageId } = params;
	depends(`page:${pageId}`);
	const { survey } = await parent();

	const currentPageIndex = Number(params.pageId);
	console.log(survey);
	const maxPageIndex = survey.pages[survey.pages.length - 1].order;

	const pageData = survey.pages[currentPageIndex - 1];

	const pageSchema = generateSchemaForPage(pageData);

	const session = await locals.auth();
	let participant_id = session?.user?.id;

	const answersResponse = await fetch(`${API_BASE_URL}/api/participants/${participant_id}/answers`);
	let answersData = {};
	if (answersResponse.ok) {
		const answers = await answersResponse.json();
		for (const item of pageData.items) {
			const answer = answers.find((a) => a.item_id === item.id && a.page_id === pageData.id);
			if (answer) {
				answersData[`item_${item.id}`] = { answer: answer.value, id: answer.id };
			}
		}
	}

	const form = await superValidate(answersData, zod(pageSchema));

	const prevPageId =
		currentPageIndex > 1 && !survey.pages[currentPageIndex - 1].back_button_disabled
			? currentPageIndex - 1
			: null;

	const nextPageId = currentPageIndex < maxPageIndex ? currentPageIndex + 1 : null;

	return {
		pageData,
		form,
		prevPageId,
		nextPageId
	};
};

export const actions: Actions = {
	updateAnswers: async ({ request, params, locals, fetch }) => {
		const { publicationUUID, pageId } = params;

		// Fetch survey data
		const publicationResponse = await fetch(
			`${API_BASE_URL}/api/publications/uuid/${publicationUUID}`
		);
		if (!publicationResponse.ok) {
			throw error(publicationResponse.status, 'Failed to fetch publication data');
		}
		const publication = await publicationResponse.json();

		const surveyResponse = await fetch(
			`${API_BASE_URL}/api/projects/${publication.project_id}/survey`
		);
		if (!surveyResponse.ok) {
			throw error(surveyResponse.status, 'Failed to fetch survey data');
		}
		const survey = await surveyResponse.json();

		const pageData = survey.pages[Number(pageId) - 1];
		const pageSchema = generateSchemaForPage(pageData);

		// Validate form data
		const formData = await request.formData();
		const navigation = formData.get('navigation');

		const form = await superValidate(formData, zod(pageSchema));
		console.log('yoo', form.valid);
		if (!form.valid) {
			return fail(400, { form });
		}

		// Get participant ID
		const session = await locals.auth();
		const participantId = session?.user?.id;
		if (!participantId) {
			throw error(401, 'Unauthorized');
		}

		// Save answers
		for (const item of pageData.items) {
			const answer = form.data[`item_${item.id}`];
			if (answer) {
				const url = answer.id
					? `${API_BASE_URL}/api/answers/${answer.id}`
					: `${API_BASE_URL}/api/answers/`;

				const answerResponse = await fetch(url, {
					method: answer.id ? 'PUT' : 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						item_id: item.id,
						participant_id: participantId,
						page_id: pageData.id,
						value: answer.answer
					})
				});

				if (!answerResponse.ok) {
					throw error(answerResponse.status, 'Failed to save answer');
				}
			}
		}

		if (navigation === 'finnish' && publication.redirect_url) {
			return redirect(303, publication.redirect_url);
		}

		if (navigation === 'finnish') {
			return { form };
		}

		// Use 303 See Other for the redirect
		return redirect(303, `/public/${publicationUUID}/${navigation}`);
	}
};
