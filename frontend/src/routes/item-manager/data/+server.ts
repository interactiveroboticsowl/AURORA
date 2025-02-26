import { API_BASE_URL } from '$lib/config';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ fetch }) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/items/export_csv`, {
            method: 'GET',
            headers: {
                'Content-Type': 'text/csv',
            },
        });

        if (!response.ok) {
            return new Response('Failed to export CSV', { status: 500 });
        }

        const csvData = await response.blob();
        return new Response(csvData, {
            headers: {
                'Content-Disposition': 'attachment; filename="items.csv"',
                'Content-Type': 'text/csv',
            }
        });
    } catch (error) {
        return new Response('Error occurred while exporting CSV', { status: 500 });
    }
};
