<script lang="ts">
	import { ChevronsUpDown, ChevronUp, ChevronDown } from 'lucide-svelte';
	import * as Collapsible from '$lib/components/ui/collapsible';
	import { Button } from '$lib/components/ui/button';
	import * as Table from '$lib/components/ui/table/index.js';
	import { page } from '$app/stores';

	interface PageData {
		id: number;
		name: string;
		description: string;
		items: ItemData[];
		order: number;
	}

	interface ItemData {
		id: number;
		title: string;
		order: number;
	}

	interface Props {
		data: PageData;
		isFirst: boolean;
		isLast: boolean;
		movePage: (pageId: number, direction: 'up' | 'down') => void;
		deletePage: (pageId: number) => void;
		deleteItem: (pageId: number, itemId: number) => void;
		reorderItem: (pageId: number, itemId: number, direction: 'up' | 'down') => void;
	}

	const { data, isFirst, isLast, movePage, deletePage, deleteItem, reorderItem }: Props = $props();
	let open = $state(false);

	$effect(() => {
		open = Number($page.params.pageId) === data.id;
	});
</script>

<Collapsible.Root class="w-full" bind:open>
	<Collapsible.Trigger asChild let:builder>
		<div class="flex items-center justify-between p-4 cursor-pointer hover:bg-accent">
			<div class="flex items-center space-x-2">
				<Button
					disabled={isFirst}
					variant="ghost"
					size="icon"
					on:click={() => movePage(data.id, 'up')}
				>
					<ChevronUp />
				</Button>
				<Button
					disabled={isLast}
					variant="ghost"
					size="icon"
					on:click={() => movePage(data.id, 'down')}
				>
					<ChevronDown />
				</Button>
				<span>{data.name}</span>
			</div>
			<div class="flex items-center space-x-2">
				<Button variant="ghost" size="icon" on:click={() => deletePage(data.id)}>🗑️</Button>
				<Button variant="outline" builders={[builder]}>
					<ChevronsUpDown class={open ? 'rotate-180 transform' : ''} />
				</Button>
			</div>
		</div>
	</Collapsible.Trigger>
	<Collapsible.Content>
		<div class="p-4">
			<h4 class="font-semibold mb-2">Description:</h4>
			<p class="mb-2">{data.description}</p>
			<h4 class="font-semibold mb-2">Items:</h4>
			<Table.Root>
				<Table.Header>
					<Table.Row>
						<Table.Head class="w-[500px]">Title</Table.Head>
						<Table.Head>Move</Table.Head>
						<Table.Head>Delete</Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each data.items as item}
						<Table.Row>
							<Table.Cell class="">{item.title}</Table.Cell>
							<Table.Cell class="flex flex-row">
								<Button variant="ghost" size="icon" on:click={() => reorderItem(data.id, item.id, 'up')}>
									<ChevronUp />
								</Button>
								<Button variant="ghost" size="icon" on:click={() => reorderItem(data.id, item.id, 'down')}>
									<ChevronDown />
								</Button>
							</Table.Cell>
							<Table.Cell>
								<Button variant="ghost" size="icon" on:click={() => deleteItem(data.id, item.id)}>🗑️</Button>
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
			<div class="flex w-full justify-center items-center">
				<Button
					class="rounded mr-1"
					href={`/projects/${$page.params.projectId}/survey/pages/${data.id}/items`}
				>
					Add item
				</Button>
			</div>
		</div>
	</Collapsible.Content>
</Collapsible.Root>
