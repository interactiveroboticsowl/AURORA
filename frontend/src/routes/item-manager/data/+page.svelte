<script lang="ts">
    import { Button } from '$lib/components/ui/button';
    async function exportCsv() {
        try {
            const response = await fetch('/item-manager/data/');

            if (!response.ok) {
                throw new Error('Failed to download CSV');
            }

            const csvData = await response.blob();

            // Trigger the download in the browser
            const url = window.URL.createObjectURL(csvData);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'items.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Error downloading CSV:', error);
        }
    }
</script>

<div class="flex h-[52px] items-center border-b border-border mb-4 pb-2">
    <h1 class="text-3xl font-bold pl-2">Data Hub</h1>
</div>

<div class="p-6 space-y-8">

    <!-- Export Survey Items Card -->
    <div class="w-full max-w-lg mx-auto space-y-4 border border-border p-6 rounded-lg shadow-md bg-background">
        <h2 class="text-2xl font-semibold">Export Survey Items</h2>
        <p class="text-sm text-muted-foreground">
            Download all survey items as a CSV file.
        </p>
        <form method="POST" action="?/exportCsv" class="flex justify-end">
            <Button
                on:click={exportCsv}
                variant="default"
                size="sm"
                class="bg-primary text-primary-foreground hover:bg-primary-foreground"
            >
                Download Items as CSV
            </Button>
        </form>
    </div>

    <!-- Import Question Items Card -->
    <div class="w-full max-w-lg mx-auto space-y-4 border border-border p-6 rounded-lg shadow-md bg-background">
        <h2 class="text-2xl font-semibold">Import Question Items</h2>
        <p class="text-sm text-muted-foreground">
            Import question items from a CSV file. Please make sure the CSV file is in the correct format.
        </p>
        <form method="POST" action="?/importCsv" enctype="multipart/form-data" class="space-y-4">
            <input 
                type="file" 
                name="file"
                accept=".csv"
                class="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary-foreground"
            />
            <div class="flex justify-end">
                <Button
                    type="submit"
                    variant="default"
                    size="sm"
                    class="bg-primary text-primary-foreground hover:bg-primary-foreground"
                >
                    Import Items from CSV
                </Button>
            </div>
        </form>
    </div>
</div>
