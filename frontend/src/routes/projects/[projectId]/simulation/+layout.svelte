<script lang="ts">
	import * as Resizable from '$lib/components/ui/resizable/index.js';
	import { Separator } from '$lib/components/ui/separator';
	import RepoForm from '$lib/components/repo/RepoForm.svelte';
	import BuildCard from '$lib/components/BuildCard.svelte';
	import { Search, PlusCircle } from 'lucide-svelte';	
	import { Button } from '$lib/components/ui/button';	
	import { Input } from '$lib/components/ui/input';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import { cn } from '$lib/utils';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import { onMount, type Snippet } from 'svelte';
	import LogTopicForm from '$lib/components/forms/log-topic/LogTopicForm.svelte';

	const projectId = $page.params.projectId;

	let { data, children } = $props<{ data: PageData; children: Snippet }>();		
	let { containers, applicationData } = $derived(data)	

	onMount(() => {
		const interval = setInterval(async () => {
			const response = await fetch(`/projects/${projectId}/build-status`);
			if (!response.ok) {
				console.log("error updating application build state")
				return;
			}

			const data = await response.json()
			console.log(data)

			if (data.status) {
				applicationData.status = data.status
			}
		}, 5000);
		//If a function is returned from onMount, it will be called when the component is unmounted.
		return () => clearInterval(interval);
	})	
</script>

<Resizable.Pane class={$page.url.pathname.includes("containers") ? "blur pointer-events-none" : ""}>
	<div class="flex h-[52px] items-center">
		<h1 class="text-2xl font-bold pl-2">Simulation</h1>
	</div>
	<Separator />
	<Resizable.PaneGroup direction="vertical">
		<Resizable.Pane defaultSize={55}>
			<div class="flex flex-grow h-full">
				<RepoForm data={data.repoFormData} />
				<Separator orientation="vertical" />
				<!-- TODO: transform to containers/newcontainer component-->
				<div class="w-full">					
					<div class="flex h-[52px] items-center justify-between px-4">
						<h1 class="text-xl font-bold">Containers</h1>
						<button
							class="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
							onclick={() => goto(`/projects/${$page.params.projectId}/simulation/containers/`)}
						>
							<PlusCircle class="mr-2 h-4 w-4" />
							Add
						</button>
					</div>
					<Separator />
					<div class="bg-background/95 supports-[backdrop-filter]:bg-background/60 p-4 backdrop-blur">
						<form>
							<div class="relative">
								<Search
									class="text-muted-foreground absolute left-2 top-[50%] h-4 w-4 translate-y-[-50%]"
								/>
								<Input placeholder="Search" class="pl-8" />
							</div>
						</form>
						<ScrollArea class="pt-2">
							<div class="flex flex-col gap-2 pt-0">
								{#each containers as container}
									<Button data-sveltekit-preload-data="hover"
										variant="ghost"
										class={cn(
											'hover:bg-accent flex flex-col items-start gap-2 rounded-lg border border-muted p-4 text-left text-sm transition-all min-h-14',
											$page.params.containerId && $page.params.containerId === container.id && 'bg-muted'
										)}
										href={`/projects/${$page.params.projectId}/simulation/containers/${container.id}`}
									>
										<div class="flex w-full flex-col gap-1">
											<div class="flex items-center gap-2">
												<div class="font-semibold">{container.name}</div>
											</div>
											<div class="text-xs font-medium text-muted-foreground">{container.dockerfile}</div>
										</div>
									</Button>
								{/each}
							</div>
						</ScrollArea>
					</div>
					<Separator />
					<div class="flex h-[52px] items-center justify-between px-4">
						<h1 class="text-xl font-bold">Logging</h1>
					</div>
					<Separator />					
					<LogTopicForm data={data.topicsFormData}></LogTopicForm>			
				</div>
			</div>
		</Resizable.Pane>
		<Resizable.Handle withHandle />
		<Resizable.Pane defaultSize={45}>			
			<BuildCard buildStatus={applicationData.status} form={data.buildFormData}/>
		</Resizable.Pane>
	</Resizable.PaneGroup>
	<Separator />	
</Resizable.Pane>
<!-- <Resizable.Handle withHandle />
<Resizable.Pane> -->
	{@render children()}
<!-- </Resizable.Pane> -->
