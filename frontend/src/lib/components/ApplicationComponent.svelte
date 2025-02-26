<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Loader2 } from 'lucide-svelte';

	interface Props {
		endpoint: string;
		checkInterval?: number; // Interval in milliseconds
	}

	let { endpoint, checkInterval = 5000 }: Props = $props();
	let isLoading = $state(true);
	let isAvailable = $state(false);
	let checkIntervalId: ReturnType<typeof setTimeout> | null = $state(null);

	async function checkEndpoint() {
		try {
			const response = await fetch(`http://${endpoint}`, { method: 'HEAD' });
			const newIsAvailable = response.ok && response.status !== 404;
			if (newIsAvailable !== isAvailable) {
				isAvailable = newIsAvailable;
				isLoading = false;
			}
		} catch (error) {
			console.error('Error checking endpoint:', error);
			if (isAvailable) {
				isAvailable = false;
				isLoading = false;
			}
		}
	}

	function startPeriodicCheck() {
		checkEndpoint(); // Check immediately
		checkIntervalId = setInterval(checkEndpoint, checkInterval);
	}

	onMount(() => {
		startPeriodicCheck();
	});

	onDestroy(() => {
		if (checkIntervalId !== null) {
			clearInterval(checkIntervalId);
		}
	});
</script>

<div class="w-full h-full">
	{#if isLoading}
		<div class="w-full h-full flex flex-col items-center justify-center bg-gray-100 rounded-lg">
			<Loader2 class="w-8 h-8 text-blue-500 animate-spin mb-2" />
			<p class="text-gray-700">Loading...</p>
		</div>
	{:else if isAvailable}
		<iframe
			src={`http://${endpoint}`}
			class="w-full h-full border-none shadow-lg rounded-lg"
			title="Content from {endpoint}"
		></iframe>
	{:else}
		<div class="w-full h-full flex items-center justify-center bg-gray-100 rounded-lg">
			<p class="text-gray-500">The requested content is not available. Checking periodically...</p>
		</div>
	{/if}
</div>
