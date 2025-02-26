import { z } from 'zod';
export const itemType = z.enum(['question', 'static_text', 'image', 'video']);
export type ItemType = z.infer<typeof itemType>;
export const questionType = z.enum([
	'free_text',
	'multiple_choice_single',
	'multiple_choice_multiple',
	'scale',
	'matrix_scale'
]);
export type QuestionType = z.infer<typeof questionType>;

export const itemTemplateSchema = z.object({
	id: z.number().optional(),
	page_id: z.number(),
	title: z.string().min(1, 'Title is required'),
	prompt: z.string().optional(),
	item_type: itemType.optional(),
	question_type: questionType.optional(),
	options: z.array(z.string()).optional(),
	scale_min: z.number().optional(),
	scale_max: z.number().optional(),
	statements: z.array(z.string()).optional(),
	matrix_options: z.array(z.string()).optional(),
	image_url: z.string().url().optional(),
	video_url: z.string().url().optional(),
	text_content: z.string().optional()
});

export type ItemTemplateSchema = z.infer<typeof itemTemplateSchema>;
