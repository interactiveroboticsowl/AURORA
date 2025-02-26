import { z } from 'zod';

const ItemAnswer = z.object({
	item_id: z.number(),
	participant_id: z.number(),
	id: z.number().optional()
});

const FreeTextAnswer = ItemAnswer.extend({
	answer: z.string()
});

const MultipleChoiceSingleAnswer = ItemAnswer.extend({
	answer: z.string()
});

const MultipleChoiceMultipleAnswer = ItemAnswer.extend({
	answer: z.array(z.string())
});

const ScaleAnswer = ItemAnswer.extend({
	answer: z.number()
});

const MatrixScaleAnswer = ItemAnswer.extend({
	answer: z.array(z.number())
});

const LikertScaleAnswer = ItemAnswer.extend({
	answer: z.number()
});

export interface Item {
	id: number;
	page_id: number;
	title: string;
	prompt?: string;
	item_type: 'question' | 'static_text' | 'image' | 'video';
	question_type?:
		| 'free_text'
		| 'multiple_choice_single'
		| 'multiple_choice_multiple'
		| 'scale'
		| 'matrix_scale'
		| 'likert_scale';
	options?: string[];
	scale_min?: number;
	scale_max?: number;
	statements?: string[];
	matrix_options?: string[];
	image_url?: string;
	video_url?: string;
	text_content?: string;
}

export interface Page {
	id: number;
	survey_id: number;
	order?: number;
	name: string;
	description?: string;
	application_enabled?: boolean;
	back_button_disabled?: boolean;
	items: Item[];
}

function questionTypeToSchema(questionType: string, item: Item) {
	switch (questionType) {
		case 'free_text':
			return FreeTextAnswer;
		case 'multiple_choice_single':
			return MultipleChoiceSingleAnswer;
		case 'multiple_choice_multiple':
			return MultipleChoiceMultipleAnswer;
		case 'scale':
			return ScaleAnswer.extend({
				answer: z
					.number()
					.min(item.scale_min || 0)
					.max(item.scale_max || 10)
			});
		case 'matrix_scale':
			return MatrixScaleAnswer.extend({
				answer: z.array(z.number()).length(item.statements?.length || 0)
			});
		case 'likert_scale':
			return LikertScaleAnswer;
		default:
			return undefined;
	}
}

export function generateSchemaForPage(page: Page) {
	const itemSchemas: Record<string, z.ZodTypeAny> = {};

	page.items.forEach((item) => {
		if (item.item_type === 'question' && item.question_type) {
			const schema = questionTypeToSchema(item.question_type, item);
			if (!schema) {
				return;
			}
			itemSchemas[`item_${item.id}`] = schema.omit({ item_id: true, participant_id: true });
		}
	});

	return z.object({
		...itemSchemas,
		redirectId: z.number().optional()
	});
}
