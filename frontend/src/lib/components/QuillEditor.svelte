<script lang="ts">
	import { onMount } from 'svelte';

	export let value: string = '';
	export let onChange: (value: string) => void;

	let quillContainer: HTMLDivElement;

	onMount(async () => {
		const quill_module = await import('quill');
		const Quill = quill_module.default;
		const quill = new Quill(quillContainer, {
			theme: 'snow',
			modules: {
				toolbar: [
					['bold', 'italic', 'underline'],
					[{ header: [1, 2, 3, false] }],
					[{ list: 'ordered' }, { list: 'bullet' }],
					['link', 'image']
				]
			}
		});

		quill.on('text-change', () => {
			const html = quill.root.innerHTML;
			onChange(html);
		});

		quill.root.innerHTML = value;
	});
</script>

<div bind:this={quillContainer} class="quill-editor"></div>

<style>
	.quill-editor {
		height: 300px;
	}
</style>

