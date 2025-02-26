import { API_BASE_URL } from '$lib/config';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    const { projectId } = params;
    // Returning the mock response for Rosbags list as part of the load function    
    const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/rosbag`);

    if (response.ok) {
        return {
            rosbags: await response.json(),
            projectId: projectId
        };    
    }

    return {
        rosbags: [],
        projectId: projectId
    }
};
