<script lang="ts">    
    import * as Resizable from '$lib/components/ui/resizable';
    import { Button } from '$lib/components/ui/button';
    import { Separator } from '$lib/components/ui/separator'; 
        import type { PageData } from './$types';
	import { LoaderCircle } from 'lucide-svelte';

    let { data } = $props<{ data: PageData }>();
	let { rosbags, projectId } = data;
    let rosbagsState = $state(rosbags.map((e: string) => true));

    async function downloadRosbag(name: string, index: number) {
        try {
            rosbagsState[index] = false
            
            const response = await fetch(`/projects/${projectId}/data/storage/${name}`);

            if (!response.ok) {
                throw new Error('Failed to download Rosbag');
            }            

            const rosbagData = await response.blob();

            // Trigger the download in the browser
            const url = window.URL.createObjectURL(rosbagData);
            const a = document.createElement('a');
            a.href = url;
            a.download = name.replace("/", "_");
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            rosbagsState[index] = true

        } catch (error) {
            console.error('Error downloading Rosbag:', error);
        }
    }

    async function initiateDownloadSurvey() {
        try {            
            const response = await fetch(`/projects/${projectId}/data`);

            if (!response.ok) {
                throw new Error('Failed to download CSV');
            }

            const rosbagData = await response.blob();

            // Trigger the download in the browser
            const url = window.URL.createObjectURL(rosbagData);
            const a = document.createElement('a');
            a.href = url;
            a.download = "survey.csv";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            console.error('Error downloading survey:', error);
        }
    }
</script>

<Resizable.Pane>
    <div class="flex h-[52px] items-center">
        <h1 class="text-2xl font-bold pl-2">Data Hub</h1>
    </div>
    <Separator />
    <div class="m-4 grid grid-cols-[auto_auto] gap-4 justify-start">
        <div class="flex flex-col gap-6">
            <div>
                <h2 class="text-xl font-semibold mb-4">Download Data</h2>
                <p class="text-sm text-muted-foreground mt-2">
                    Download the survey data and participant responses in CSV format for offline analysis.
                </p>
                <div class="flex gap-2 mt-4">
                    <Button
                        size="sm"
                        class="bg-primary text-primary-foreground hover:bg-primary-foreground"
                        on:click={() => initiateDownloadSurvey()}
                    >
                        Download Survey Data including Answers
                    </Button>                    
                </div>
            </div>

            <div>
                <h2 class="text-xl font-semibold mb-4">Rosbag Files</h2>
                <Separator class="my-4 border-border" />
                <p class="text-sm text-muted-foreground mt-2">
                    Download recorded ROS bag files to review experiment data from simulations.
                </p>
                <div class="p-4">
                    {#if rosbags.length > 0}
                        <ul class="space-y-4">
                            {#each rosbags as rosbag, index}
                                <li class="border border-border p-4 rounded flex justify-between items-center">
                                    <div>
                                        <h2 class="font-semibold">{rosbag}</h2>
                                    </div>
                                    <div class="space-x-2">
                                        <Button
                                            disabled={!rosbagsState[index]}
                                            variant="default"
                                            size="sm"
                                            class="bg-primary text-primary-foreground hover:bg-primary-foreground}"
                                            on:click={() => downloadRosbag(rosbag, index)}
                                        >
                                            {#if !rosbagsState[index]}
                                            <LoaderCircle class="mr-2 h-4 w-4 animate-spin" />
                                            {/if}
                                            Download
                                        </Button>
                                    </div>
                                </li>
                            {/each}
                        </ul>
                    {:else}
                        <p>No rosbags available for download.</p>
                    {/if}
                </div>
            </div>
        </div>
    </div>
</Resizable.Pane>
