import { API_BASE_URL } from "$lib/config";
import { json } from "@sveltejs/kit";

export async function GET({ params }) {
    const projectId = params.projectId
    const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/application/`);

    if (!response.ok) {
        console.log("error updating application build state")
    }

    return json({ "status": (await response.json()).status })
}