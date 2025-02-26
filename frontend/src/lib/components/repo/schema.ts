import { z } from 'zod';

export const gitRepoSchema = z.object({
	git_url: z.string().startsWith('https://').endsWith('.git'),
	access_token: z.string(),
	git_branch: z.string(),
	application_id: z.number(),
	id: z.number()
});

export type GitRepoSchema = typeof gitRepoSchema;
