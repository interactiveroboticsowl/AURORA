import type { PageServerLoad, Actions } from './$types';
import { API_BASE_URL } from '$lib/config';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, fetch }) => {
    const { pageId } = params;

    if (!pageId) {
        throw fail(404, 'Page not found');
    }

    // Fetch all items
    const response = await fetch(`${API_BASE_URL}/api/items/`);
    if (!response.ok) {
        throw fail(500, 'Failed to load items');
    }

    const items = await response.json();

    return { items, pageId };
};

export const actions: Actions = {
    addItemToPage: async ({ params, request }) => {
        const { pageId } = params;
        const formData = await request.formData();
        const itemId = formData.get('item_id');

        if (!pageId || !itemId) {
            return fail(400, { error: 'Page ID and Item ID are required' });
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/pages/${pageId}/items/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ item_id: Number(itemId) }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                return fail(response.status, { error: errorData.detail || 'Failed to add item' });
            }

            return { success: true };
        } catch (error) {
            console.error('Error adding item to page:', error);
            return fail(500, { error: 'An unexpected error occurred while adding the item' });
        }
    },
};
