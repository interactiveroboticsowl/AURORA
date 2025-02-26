import { API_BASE_URL } from '$lib/config';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ fetch, params }) => {
    const { projectId } = params
    try {
        const getProjectSurvey = await fetch(`${API_BASE_URL}/api/projects/${projectId}/survey`);
        if (!getProjectSurvey.ok) {
            throw new Error('Failed to download CSV');
        }
        const survey = await getProjectSurvey.json()
        
        const response = await fetch(`${API_BASE_URL}/api/surveys/${survey.id}/export?format=csv&include_answers=true`, {
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
                'Content-Disposition': 'attachment; filename="survey.csv"',
                'Content-Type': 'text/csv',
            }
        });
    } catch (error) {
        return new Response('Error occurred while exporting CSV', { status: 500 });
    }
};
