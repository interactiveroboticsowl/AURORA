import { z } from 'zod';

export const projectSchema = z.object({
	name: z.custom<`${number}px`>((val) => {
		return typeof val === "string" ? /(\D)/.test(val) && !/(\s)/.test(val) : false;
	}, { message: "Must contain at least one non-numeric character and no whitespaces!"})
});

export type ProjectSchema = typeof projectSchema;
