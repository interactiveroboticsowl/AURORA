import { itemSchema } from '$lib/components/forms/survey/schema';
import { type Actions } from '@sveltejs/kit';
import { fail, superValidate, message } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config';
import { setFlash } from 'sveltekit-flash-message/server';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const itemId = params.itemId;

	const response = await fetch(`${API_BASE_URL}/api/items/${itemId}`);
	if (!response.ok) {
		throw new Error('Failed to load item');
	}

	const item = await response.json();

	const form = await superValidate(item, zod(itemSchema));

	return { form };
};

export const actions: Actions = {
	default: async (event) => {
		const form = await superValidate(event, zod(itemSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const response = await event.fetch(`${API_BASE_URL}/api/items/${form.data.id}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(form.data)
		});

		if (!response.ok) {
			const errorData = await response.json();
			return message(
				form,
				{ message: errorData.message || 'Error occurred', type: 'error' },
				{ status: response.status }
			);
		}

		return message(form, { message: 'Item updated', type: 'success' });
	}
};
