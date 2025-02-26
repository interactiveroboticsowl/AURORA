<script lang="ts">
    import { Separator } from '$lib/components/ui/separator';
    import type { PageData } from './$types';
    import { Button } from '$lib/components/ui/button';
    import { enhance } from '$app/forms';

    export let data: PageData;

    let { items, pageId } = data;
    let searchQuery = '';

    function filteredItems() {
        if (!searchQuery) {
            return items; 
        }
        const lowerCaseQuery = searchQuery.toLowerCase();
        return items.filter(item =>
            item.title.toLowerCase().includes(lowerCaseQuery) ||
            (item.prompt && item.prompt.toLowerCase().includes(lowerCaseQuery)) ||
            (item.item_type && item.item_type.toLowerCase().includes(lowerCaseQuery)) ||
            (item.question_type && item.question_type.toLowerCase().includes(lowerCaseQuery))
        );
    }
</script>

<div class="flex h-[52px] items-center">
    <h1 class="text-2xl font-bold pl-2">Add Items to Page</h1>
</div>
<Separator />

<div class="p-4">
    <input
        type="text"
        placeholder="Search items..."
        bind:value={searchQuery}
        class="border-input bg-background ring-offset-background placeholder:text-muted-foreground flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none"
    />
</div>

<div class="p-4">
    {#if filteredItems().length > 0}
        <ul class="space-y-4">
            {#each filteredItems() as item}
                <li class="border border-border p-4 rounded flex justify-between items-center">
                    <div>
                        <h2 class="font-semibold">{item.title}</h2>
                        {#if item.prompt}
                            <p class="text-muted">{item.prompt}</p>
                        {/if}
                        <p class="text-sm italic">Item Type: {item.item_type}</p>
                        {#if item.question_type}
                            <p class="text-sm italic">Question Type: {item.question_type}</p>
                        {/if}
                        <p class="text-sm italic">ID: {item.id}</p>
                        {#if item.options && item.options.length > 0}
                            <p class="text-sm">Options: {item.options.join(', ')}</p>
                        {/if}
                        {#if item.statements && item.statements.length > 0}
                            <p class="text-sm">Statements: {item.statements.join(', ')}</p>
                        {/if}
                    </div>
                    <div class="space-x-2">
                        <form method="post" action="?/addItemToPage" use:enhance>
                            <input type="hidden" name="item_id" value={item.id} />
                            <Button variant="default" type="submit">
                                Add to Page
                            </Button>
                        </form>
                    </div>
                </li>
            {/each}
        </ul>
    {:else}
        <p>No items found. Please add some items.</p>
    {/if}
</div>