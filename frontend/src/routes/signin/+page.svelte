<script lang="ts">
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { page } from '$app/stores';
	import { INVALID_USERNAME_OR_PASSWORD_CODE } from '$lib/constants';

	const redirectUrl = $page.url.searchParams.get('callbackUrl')
		? $page.url.searchParams.get('callbackUrl')
		: '/projects';
</script>

<div class="w-screen h-screen flex justify-center items-center">
	<form method="POST" action="/auth/callback/admin-credentials">
		<input type="hidden" name="callbackUrl" value={redirectUrl} />
		<Card.Root class="w-full max-w-sm">
			<Card.Header>
				<Card.Title class="text-2xl">Login</Card.Title>
				<Card.Description>Enter your credentials below to login to your account.</Card.Description>
			</Card.Header>
			<Card.Content class="grid gap-4">
				<div class="grid gap-2">
					<Label for="username">Username</Label>
					<Input id="username" name="username" type="user" required />
				</div>
				<div class="grid gap-2">
					<Label for="password">Password</Label>
					<Input id="password" name="password" type="password" required />
				</div>

				{#if $page.url.searchParams.get('code') === INVALID_USERNAME_OR_PASSWORD_CODE}
					<p class="text-red-500">Invalid Username or Password. Please try again.</p>
				{/if}
			</Card.Content>
			<Card.Footer>
				<Button type="submit" class="w-full">Sign in</Button>
			</Card.Footer>
		</Card.Root>
	</form>
</div>
