<script lang="ts">
	export let url: string = '';
	export let title: string = '';
</script>

<div class="flex justify-center items-start p-4">
	<iframe
		src={url}
		{title}
		class="w-full max-w-4xl h-[600px] border-none shadow-lg rounded-lg"
		allowfullscreen
	></iframe>
</div>
