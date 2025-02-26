import { type Actions } from '@sveltejs/kit';
import { signIn } from '../../auth';

export const load = async (event) => {
	const session = await event.locals.auth();
	if (session) {
		return {
			status: 302,
			headers: {
				location: '/projects'
			}
		};
	}
};

export const actions = {
	default: (event) => {
		return signIn(event);
	}
} satisfies Actions;
