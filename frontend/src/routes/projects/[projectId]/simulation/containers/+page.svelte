<script lang="ts">
	import * as Resizable from '$lib/components/ui/resizable/index.js';
	import ChevronLeft from "lucide-svelte/icons/chevron-left";
	import { Button } from "$lib/components/ui/button/index.js";
	import { Separator } from '$lib/components/ui/separator';
	import ContainerForm from '$lib/components/forms/container/ContainerForm.svelte';
	import type { PageData } from './$types';	
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { data } = $props<{ data: PageData }>();
</script>


<Resizable.Handle withHandle />
<Resizable.Pane>
	<div class="flex">
		<div class="flex h-[52px] items-center text-xl pl-4 justify-between">
			<Button variant="ghost" size="icon" onclick={() => goto(`/projects/${$page.params.projectId}/simulation`)}>
				<ChevronLeft class="h-4 w-4" />
			</Button>
			New Container
		</div>
	</div>
<Separator />
<div class="p-4 w-full">
	<ContainerForm data={data.containerForm} action="?/create" />
</div>
</Resizable.Pane>