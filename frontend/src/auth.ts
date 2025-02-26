import { API_BASE_URL } from '$lib/config';
import { SvelteKitAuth, CredentialsSignin } from '@auth/sveltekit';
import CredentialsProvider from '@auth/sveltekit/providers/credentials';
import { env } from '$env/dynamic/private';
import { INVALID_USERNAME_OR_PASSWORD_CODE } from '$lib/constants';

export class InvalidLoginError extends CredentialsSignin {
	code = INVALID_USERNAME_OR_PASSWORD_CODE;
}

export const config = {
	providers: [
		CredentialsProvider({
			id: 'admin-credentials',
			name: 'Admin Credentials',
			credentials: {
				username: { label: 'Username', type: 'text' },
				password: { label: 'Password', type: 'password' }
			},
			async authorize(credentials) {
				const { username, password } = credentials;
				console.log(credentials);

				if (typeof username !== 'string' || typeof password !== 'string') {
					throw new InvalidLoginError();
				}

				const response = await fetch(`${env.AUTH_URL}/api/auth/verify`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ username: username, password: password })
				});

				console.log(response);
				if (!response.ok) {
					throw new InvalidLoginError();
				}

				const data = await response.json()
				const id = String(data.id);
				return { id, type: 'user', is_admin: data.is_admin };

				return null;
			}
		}),
		CredentialsProvider({
			id: 'end-user-credentials',
			name: 'End User Credentials',
			credentials: {
				id: { type: 'text' }
			},
			async authorize(credentials) {
				const response = await fetch(`${env.AUTH_URL}/api/participants/${credentials.id}`);
				if (response.ok) {
					const data = await response.json();
					return { id: data.id, type: 'participant' };
				}
				return null;
			}
		})
	],
	callbacks: {
		async jwt({ token, user }) {
			if (user) {
				token.id = user.id as string;
				token.type = user.type;
				if (user.type === 'user') {
					token.is_admin = user.is_admin;
				}
			}
			return token;
		},
		async session({ session, token }) {
			session.user.id = token.id;
			session.user.type = token.type;
			if (token.type === 'user') {
				session.user.is_admin = token.is_admin;
			}
			return session;
		}
	},
	trustHost: true,
	secret: env.AUTH_SECRET,
	basePath: env.AUTH_URL,	
	pages: {
		signIn: '/signin'
	}
};

export const { handle, signIn, signOut } = SvelteKitAuth(config);
