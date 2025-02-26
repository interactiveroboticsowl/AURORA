import { CircleHelp, Type, Image, Film } from 'lucide-svelte';

export const ITEM_TYPES = [
	{ value: 'question', label: 'Question', icon: CircleHelp },
	{ value: 'static_text', label: 'Static Text', icon: Type },
	{ value: 'image', label: 'Image', icon: Image },
	{ value: 'video', label: 'Video', icon: Film }
];

export const QUESTION_TYPES = [
	{ value: 'free_text', label: 'Free Text' },
	{ value: 'multiple_choice_single', label: 'Multiple Choice Single' },
	{ value: 'multiple_choice_multiple', label: 'Multiple Choice Multiple' },
	{ value: 'scale', label: 'Scale' },
	{ value: 'matrix_scale', label: 'Matrix Scale' },
	{ value: 'likert_scale', label: 'Likert Scale' }
];
