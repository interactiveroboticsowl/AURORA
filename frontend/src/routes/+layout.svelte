<script lang="ts">
	import '../app.pcss'; // Ensure this path is correct
	import { ModeWatcher } from 'mode-watcher';
	import type { Snippet } from 'svelte';
	import { getFlash } from 'sveltekit-flash-message';

	import { Toaster } from '$lib/components/ui/sonner';
	import { toast } from 'svelte-sonner';
	import { page } from '$app/stores';

	interface Props {
		children: Snippet;
	}

	let { children }: Props = $props();

	const flash = getFlash(page);

	$effect(() => {
		if ($flash) {
			switch ($flash.type) {
				case 'success':
					toast.success($flash.message);
					break;
				case 'error':
					toast.error($flash.message);
					break;
				default:
					toast($flash.message);
					break;
			}

			$flash = undefined;
		}
	});
</script>

<ModeWatcher />
<Toaster />
<div class="relative flex min-h-screen flex-col bg-background">
	<div class="flex-1 flex">
		<main class="flex-1">
			{@render children()}
		</main>
	</div>
</div>
