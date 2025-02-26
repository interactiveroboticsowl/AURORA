import { json, fail } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { API_BASE_URL } from '$lib/config';
import { invalidate } from '$app/navigation';

export const POST: RequestHandler = async ({ request, params, url }) => {
	const action = url.searchParams.get('action');
	const surveyId = params.projectId;

	try {
		if (action === 'reorderPage') {
			const data = await request.json();
			const updatedPageOrder = data.pageOrder;

			const response = await fetch(`${API_BASE_URL}/api/surveys/${surveyId}/pages/order`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(updatedPageOrder)
			});

			if (!response.ok) {
				const errorData = await response.json();
				return fail(response.status, { error: errorData.message });
			}

			return json({ success: true });
		}

		if (action === 'deletePage') {
			const { pageId } = await request.json();

			const response = await fetch(`${API_BASE_URL}/api/surveys/${surveyId}/pages/${pageId}`, {
				method: 'DELETE'
			});

			if (!response.ok) {
				const errorData = await response.json();
				return fail(response.status, { error: errorData.message });
			}

			return json({ success: true });
		}

		if (action === 'reorderItem') {
			const data = await request.json();
			const { pageId, updatedItemOrders } = data;

			const response = await fetch(`${API_BASE_URL}/api/pages/${pageId}/items/order`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(updatedItemOrders)
			});

			if (!response.ok) {
				const errorData = await response.json();
				return fail(response.status, { error: errorData.message });
			}

			return json({ success: true });
		}

		if (action === 'deleteItem') {
			const { pageId, itemId } = await request.json();

			const response = await fetch(`${API_BASE_URL}/api/pages/${pageId}/items/${itemId}`, {
				method: 'DELETE'
			});

			if (!response.ok) {
				const errorData = await response.json();
				return fail(response.status, { error: errorData.message });
			}

			return json({ success: true });
		}

		return fail(400, { error: 'Invalid action' });
	} catch (error) {
		return fail(500, { error: 'An error occurred while processing the request.' });
	}
};
