import { API_BASE_URL } from '$lib/config';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ fetch, params }) => {
    const { objectSlug } = params
    try {
        const response = await fetch(encodeURI(`${API_BASE_URL}/api/storage/download/${objectSlug}`), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/octet-stream',
            },
        });

        if (!response.ok) {
            return new Response('Failed to export CSV', { status: 500 });
        }

        const csvData = await response.blob();
        return new Response(csvData, {
            headers: {
                'Content-Disposition': `attachment; filename=${objectSlug?.replace("/", "_")}`,
                'Content-Type': 'application/octet-stream',
            }
        });
    } catch (error) {
        return new Response('Error occurred while exporting rosbag', { status: 500 });
    }
};
