<script lang="ts">
    import { goto } from '$app/navigation';
    import { Button } from '$lib/components/ui/button';
    import { Plus, List } from 'lucide-svelte'; 

    function navigateTo(path: string) {
        goto(path);
    }
</script>

<div class="flex h-[52px] items-center">
	<h1 class="text-2xl font-bold pl-2">Item Manager</h1>
</div>

<div class="p-6 bg-background border border-border rounded-lg shadow-lg space-y-6">
    <p class="text-muted-foreground text-sm">
        Use the navigation on the left to create new items or manage existing items.
    </p>

    <div class="mt-8 flex space-x-4">
        <Button 
            variant="default" 
            class="bg-primary text-primary-foreground hover:bg-primary-foreground flex items-center space-x-2" 
            on:click={() => navigateTo('/item-manager/create')}
        >
            <Plus class="w-4 h-4" />
            <span>Create New Item</span>
        </Button>
        
        <Button 
            variant="secondary" 
            class="bg-secondary text-secondary-foreground hover:bg-secondary-foreground flex items-center space-x-2" 
            on:click={() => navigateTo('/item-manager/manage')}
        >
            <List class="w-4 h-4" />
            <span>Manage Items</span>
        </Button>
    </div>
</div>
