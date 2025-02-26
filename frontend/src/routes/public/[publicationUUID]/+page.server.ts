import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ parent, params }) => {
	const uuid = params.publicationUUID;
	const { survey } = await parent();

	if (survey) {
		redirect(303, `/public/${uuid}/1`);
	}
};
