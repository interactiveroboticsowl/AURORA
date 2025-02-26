import { z } from 'zod';

export const containerFormSchema = z.object({
	id: z.number().optional(),
	name: z
		.string()
		.min(1, 'Name is required')
		.regex(/^[a-z0-9][a-z0-9-]*[a-z0-9]$/)
		.max(53),
	dockerfile: z.string().min(1, 'Dockerfile path is required'),
	ports: z
		.array(
			z.object({
				internal_port: z.number().int().positive('Container port must be a positive integer'),
				external_port: z.number().int().positive('Host port must be a positive integer').optional()
			})
		)
		.optional()
		.default([])
});

export type ContainerFormSchema = z.infer<typeof containerFormSchema>;
