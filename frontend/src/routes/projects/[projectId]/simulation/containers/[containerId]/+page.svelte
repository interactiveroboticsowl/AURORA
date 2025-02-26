<script lang="ts">
	import * as Resizable from '$lib/components/ui/resizable/index.js';
	import ChevronLeft from "lucide-svelte/icons/chevron-left";
	import { Button } from "$lib/components/ui/button/index.js"
	import { Trash2 } from 'lucide-svelte';
	import ContainerForm from '$lib/components/forms/container/ContainerForm.svelte';
	import { Separator } from '$lib/components/ui/separator';
	import type { PageData } from './$types';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data } = $props<{ data: PageData }>();	
	let containerForm = $derived(data.containerForm);
</script>

<Resizable.Handle withHandle />
<Resizable.Pane>
<div class="flex h-[52px] items-center text-xl pl-4 justify-between">
	<Button variant="ghost" size="icon" onclick={() => goto(`/projects/${$page.params.projectId}/simulation`)}>
		<ChevronLeft class="h-4 w-4" />
	</Button>
	Container {containerForm.data.name}
	<!-- TODO: use enhance and do not reload page -->
	<form method="POST" action="?/delete" class="mr-2">
		<button
			class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
		>
			<Trash2 class="mr-2 h-4 w-4" />
			Delete
		</button>
		<input type="hidden" value={containerForm.data.id} name="id" />
	</form>
</div>
<Separator />
<div class="p-4 w-full">
	<ContainerForm data={containerForm} action="?/update" />
</div>
</Resizable.Pane>
