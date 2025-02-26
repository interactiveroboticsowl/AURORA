<script lang="ts">
	import * as Form from '$lib/components/ui/form/index.js';
	import type { Item } from '$lib/components/survey/schemaGenerator';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Table from '$lib/components/ui/table';
	import { Input } from '$lib/components/ui/input';

	interface Props {
		form: any;
		item: Item;
		value?: number[];
	}

	let { form, item, value = $bindable() }: Props = $props();

	let matrixValue = $state(value.length ? value : new Array(item.statements.length).fill(-1));

	$effect(() => {
		value = matrixValue;
	});

	function handleChange(statementIndex: number, optionIndex: number) {
		matrixValue[statementIndex] = optionIndex;
	}
</script>

<Card.Root class="mx-2">
	<Form.Field {form} name={`item_${item.id}`}>
		<Form.Control let:attrs>
			<Card.Header>
				<Card.Title>{item.title}</Card.Title>
				{#if item.prompt}
					<Card.Description>{item.prompt}</Card.Description>
				{/if}
			</Card.Header>
			<Card.Content {...attrs}>
				<Table.Root>
					<Table.Header>
						<Table.Row>
							<Table.Head class="w-[200px]"></Table.Head>
							{#each item.matrix_options as option}
								<Table.Head>{option}</Table.Head>
							{/each}
						</Table.Row>
					</Table.Header>
					<Table.Body>
						{#each item.statements as statement, statementIndex}
							<Table.Row>
								<Table.Cell class="font-medium">{statement}</Table.Cell>
								{#each item.matrix_options as _, optionIndex}
									<Table.Cell>
										<Input
											class="w-[12px]"
											type="radio"
											checked={matrixValue[statementIndex] === optionIndex}
											on:change={() => handleChange(statementIndex, optionIndex)}
										/>
									</Table.Cell>
								{/each}
							</Table.Row>
						{/each}
					</Table.Body>
				</Table.Root>
			</Card.Content>
		</Form.Control>
		<Form.FieldErrors />
	</Form.Field>
</Card.Root>
