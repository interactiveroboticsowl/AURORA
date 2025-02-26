import { type Handle, redirect } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

import { handle as authenticationHandle } from './auth';

const authorizationHandle: Handle = async ({ resolve, event }) => {
	if (
		event.url.pathname.startsWith('/item-manager') ||
		event.url.pathname.startsWith('/projects')
	) {
		const session = await event.locals.auth();
		if (!session || !session.user || session.user.type !== 'user' || !session.user.is_admin) {
			throw redirect(303, '/auth/signin');
		}
	}

	return resolve(event);
};

const defaultRedirectHandle: Handle = async ({resolve, event}) => {
	if (event.url.pathname.trim() === "/" || event.url.pathname.trim() === "") {
		throw redirect(301, '/projects')
	}

	return resolve(event);
}

export const openapiTypeScriptHandle: Handle = async ({ event, resolve }) => {
	return resolve(event, {
		filterSerializedResponseHeaders(name) {
			// SvelteKit doesn't serialize any headers on server-side fetches by default but openapi-fetch uses this header for empty responses.
			return name === 'content-length';
		}
	});
};

export const handle: Handle = sequence(
	authenticationHandle,
	defaultRedirectHandle,
	authorizationHandle,
	openapiTypeScriptHandle
);
