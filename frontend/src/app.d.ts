// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
	namespace App {
		interface PageData {
			flash?: { type: 'success' | 'error'; message: string };
		}
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}
import { DefaultSession } from '@auth/core/types';

declare module '@auth/core/types' {
	interface User {
		id: string;
		type: 'user' | 'participant';
		is_admin?: boolean;
	}
}

declare module '@auth/core/jwt' {
	interface JWT {
		id: string;
		type: 'user' | 'participant';
		is_admin?: boolean;
	}
}
export {};
