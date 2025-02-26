import { fail, error } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { API_BASE_URL } from '$lib/config';

// Loading items
export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const response = await fetch(`${API_BASE_URL}/api/items/`);

		if (!response.ok) {
			throw error(500, 'Failed to load items');
		}

		const items = await response.json();
		return { items };
	} catch (err) {
		return fail(500, { error: 'An error occurred while fetching items' });
	}
};

// Handling delete action
export const actions: Actions = {
	deleteItem: async ({ request }) => {
		const formData = await request.formData();
		const itemId = formData.get('itemId');

		if (!itemId) {
			return fail(400, { error: 'Item ID is required' });
		}

		try {
			const response = await fetch(`${API_BASE_URL}/api/items/${itemId}`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				const errorData = await response.json();
				return fail(response.status, { error: errorData.detail || 'Failed to delete item' });
			}

			return { success: true };
		} catch (err) {
			return fail(500, { error: 'An error occurred while deleting the item' });
		}
	}
};
