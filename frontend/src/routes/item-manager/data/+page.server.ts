import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { API_BASE_URL } from '$lib/config';
import { itemSchema } from '$lib/components/forms/survey/schema';

export const load: PageServerLoad = async () => {
    const form = await superValidate({}, zod(itemSchema));
    return { form };
};

export const actions: Actions = {
    createItem: async (event) => {
        const form = await superValidate(event, zod(itemSchema));

        if (!form.valid) {
            return fail(400, { form });
        }

        const response = await event.fetch(`${API_BASE_URL}/api/items/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(form.data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            return fail(response.status, {
                form,
                error: errorData.message || 'Error occurred'
            });
        }

        return { form };
    },
    importCsv: async (event) => {
        const data = await event.request.formData();
        const file = data.get('file');

        if (!file || !(file instanceof Blob)) {
            return fail(400, { error: 'No file selected or incorrect file format' });
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await event.fetch(`${API_BASE_URL}/api/items/import_csv`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                return fail(response.status, { error: errorData.message || 'Failed to import CSV' });
            }

            return { success: true };
        } catch (error) {
            return fail(500, { error: 'An error occurred while importing CSV' });
        }
    }
};