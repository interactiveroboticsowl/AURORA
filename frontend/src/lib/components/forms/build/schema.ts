import { z } from 'zod';

export const buildSchema = z.object({
	ros_version: z.string()
});

export type BuildSchema = typeof buildSchema;
