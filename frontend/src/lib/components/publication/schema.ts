import { z } from 'zod';

export const publicationSchema = z.object({
	id: z.number().optional(),
	project_id: z.number(),
	name: z.string(),
	start_date: z.string(),
	end_date: z.string().optional(),
	application_only: z.boolean().default(false),
	collect_data: z.boolean().default(true),
	redirect_url: z.string().url().optional(),
	allow_anonymous: z.boolean().default(false)
});

export type PublicationSchema = typeof publicationSchema;
