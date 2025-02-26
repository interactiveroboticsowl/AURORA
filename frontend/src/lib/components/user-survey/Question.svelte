<script lang="ts">
	import { ItemType, QuestionType } from '$lib/api/user_survey_api';
	import type { Question } from '$lib/api/user_survey_api';

	export let question: Question;

	let answer: string | number | string[] | Record<string, string> = ''; // Adjust to accommodate multiple-choice arrays

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		answer = target.value;
	}

	function handleScaleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		answer = Number(target.value);
	}

	function handleMatrixInput(statement: string, value: string) {
		if (typeof answer === 'object' && answer !== null) {
			(answer as Record<string, string>)[statement] = value;
		}
	}

	function handleMultipleChoice(option: string) {
		if (Array.isArray(answer)) {
			if (answer.includes(option)) {
				answer = answer.filter((o) => o !== option); // Remove option if already selected
			} else {
				answer = [...answer, option]; // Add option if not selected
			}
		} else {
			answer = [option]; // If answer is not an array, initialize it as an array
		}
	}
</script>

<!-- Ensure this component only renders if item_type is "question" -->
{#if question.item_type === ItemType.Question}
	<div class="question mb-6">
		<label for={`question-${question.id}`} class="block text-lg font-semibold mb-2"
			>{question.prompt}</label
		>

		{#if question.question_type === QuestionType.FreeText}
			<input
				id={`question-${question.id}`}
				type="text"
				bind:value={answer}
				on:input={handleInput}
				class="w-full p-3 border border-border rounded-md bg-input text-foreground"
			/>
		{:else if question.question_type === QuestionType.MultipleChoiceSingle}
			<div>
				{#each question.options ?? [] as option}
					<div>
						<label class="flex items-center space-x-3">
							<input
								type="radio"
								name={`question-${question.id}`}
								value={option}
								bind:group={answer}
								class="form-radio text-primary"
							/>
							<span>{option}</span>
						</label>
					</div>
				{/each}
			</div>
		{:else if question.question_type === QuestionType.MultipleChoiceMultiple}
			<div>
				{#each question.options ?? [] as option}
					<div>
						<label class="flex items-center space-x-3">
							<input
								type="checkbox"
								value={option}
								on:change={() => handleMultipleChoice(option)}
								class="form-checkbox text-primary"
							/>
							<span>{option}</span>
						</label>
					</div>
				{/each}
			</div>
		{:else if question.question_type === QuestionType.Scale}
			<div>
				<input
					id={`question-${question.id}`}
					type="range"
					min={question.scale_min}
					max={question.scale_max}
					bind:value={answer}
					on:input={handleScaleInput}
					class="w-full"
				/>
				<div class="text-sm text-muted-foreground mt-2">Selected: {answer}</div>
			</div>
		{:else if question.question_type === QuestionType.MatrixScale}
			<div class="overflow-x-auto">
				<table
					class="min-w-full table-auto border border-border rounded-md bg-input text-foreground"
				>
					<thead>
						<tr>
							<th class="p-2 border-b border-border text-left w-2/5">Statement</th>
							{#each question.matrix_options ?? [] as option}
								<th class="p-2 border-b border-border text-center w-1/12">{option}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each question.statements ?? [] as statement}
							<tr>
								<td class="p-2 border-b border-border align-middle">{statement}</td>
								{#each question.matrix_options ?? [] as option}
									<td class="p-2 border-b border-border text-center align-middle">
										<input
											type="radio"
											name={`question-${question.id}-${statement}`}
											value={option}
											on:change={() => handleMatrixInput(statement, option)}
											class="form-radio text-primary"
										/>
									</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else if question.question_type === QuestionType.LikertScale}
			<div class="overflow-x-auto">
				<table
					class="min-w-full table-auto border border-border rounded-md bg-input text-foreground"
				>
					<thead>
						<tr>
							<th class="p-2 border-b border-border text-left w-2/5">Statement</th>
							{#each ['1: Strongly Disagree', '2: Disagree', '3: Neutral', '4: Agree', '5: Strongly Agree'] as option}
								<th class="p-2 border-b border-border text-center w-1/12">{option}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each question.statements ?? [] as statement}
							<tr>
								<td class="p-2 border-b border-border align-middle">{statement}</td>
								{#each ['1', '2', '3', '4', '5'] as option}
									<td class="p-2 border-b border-border text-center align-middle">
										<input
											type="radio"
											name={`question-${question.id}-${statement}`}
											value={option}
											on:change={() => handleMatrixInput(statement, option)}
											class="form-radio text-primary"
										/>
									</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
{/if}
