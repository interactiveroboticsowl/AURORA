import { z } from 'zod';

export const logTopicFormSchema = z.object({
	topics: z
		.array(
			z.string()
		)
		.optional()
		.default([])
});

export type LogTopicFormSchema = z.infer<typeof logTopicFormSchema>;
