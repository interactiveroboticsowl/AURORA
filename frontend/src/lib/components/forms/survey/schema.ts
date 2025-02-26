import { z } from 'zod';
import { questionType, itemType } from '$lib/components/forms/item-template/schema';

export const surveySchema = z.object({
	id: z.number().optional(),
	project_id: z.number(),
	title: z.string().min(1, 'Title is required'),
	description: z.string().optional()
});

export type SurveySchema = z.infer<typeof surveySchema>;

export const pageSchema = z.object({
	id: z.number().optional(),
	survey_id: z.number(),
	order: z.number(),
	name: z.string().min(1, 'Name is required'),
	description: z.string().optional(),
	application_enabled: z.boolean().default(false),
	back_button_disabled: z.boolean().default(false)
});

export type PageSchema = z.infer<typeof pageSchema>;

export const itemSchema = z
	.object({
		id: z.number().optional(),
		page_id: z.number(),
		title: z.string().min(1, 'Title is required'),
		prompt: z.string().optional(),
		item_type: itemType,
		question_type: questionType.optional(),
		options: z.array(z.string()).optional(),
		scale_min: z.number().optional(),
		scale_max: z.number().optional(),
		statements: z.array(z.string()).optional(),
		matrix_options: z.array(z.string()).optional(),
		image_url: z.string().optional(),
		video_url: z.string().optional(),
		text_content: z.string().optional()
	})
	.refine((data) => !(data.item_type === 'question' && !data.question_type), {
		message: 'Question type is required for question items',
		path: ['question_type']
	})
	.refine((data) => !(data.item_type === 'static_text' && !data.text_content), {
		message: 'Text content is required for static text items',
		path: ['text_content']
	})
	.refine((data) => !(data.item_type === 'image' && !data.image_url), {
		message: 'Image URL is required for image items',
		path: ['image_url']
	})
	.refine((data) => !(data.item_type === 'video' && !data.video_url), {
		message: 'Video URL is required for video items',
		path: ['video_url']
	})
	.refine(
		(data) => {
			if (data.item_type === 'question' && data.question_type) {
				switch (data.question_type) {
					case 'multiple_choice_single':
					case 'multiple_choice_multiple':
					case 'likert_scale':
						return data.options && data.options.length > 0;
					default:
						return true;
				}
			}
			return true;
		},
		{
			message: 'Options are required for multiple choice and Likert scale questions',
			path: ['options']
		}
	)
	.refine(
		(data) => {
			if (data.item_type === 'question' && data.question_type === 'scale') {
				return data.scale_min !== undefined && data.scale_max !== undefined;
			}
			return true;
		},
		{
			message: 'Scale min and max are required for scale questions',
			path: ['scale_min', 'scale_max']
		}
	)
	.refine(
		(data) => {
			if (data.item_type === 'question' && data.question_type === 'matrix_scale') {
				return (
					data.statements &&
					data.statements.length > 0 &&
					data.matrix_options &&
					data.matrix_options.length > 0
				);
			}
			return true;
		},
		{
			message: 'Statements and matrix options are required for matrix scale questions',
			path: ['statements', 'matrix_options']
		}
	);

export type ItemSchema = z.infer<typeof itemSchema>;
