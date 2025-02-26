<script lang="ts">
	import { page } from '$app/stores';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Form from '$lib/components/ui/form/index.js';
	import { Input } from '$lib/components/ui/input';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Button, buttonVariants } from '$lib/components/ui/button/index.js';
	import { cn } from '$lib/utils';
	import { CirclePlus } from 'lucide-svelte';
	import { type PublicationSchema, publicationSchema } from '$lib/components/publication/schema';
	import { type SuperValidated, superForm, type Infer } from 'sveltekit-superforms';
	import SuperDebug from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import {
		CalendarDate,
		DateFormatter,
		type DateValue,
		getLocalTimeZone,
		parseDate,
		today
	} from '@internationalized/date';
	import { CalendarIcon } from 'lucide-svelte';

	import * as Popover from '$lib/components/ui/popover/index.js';

	import { Calendar } from '$lib/components/ui/calendar/index.js';
	import { invalidate } from '$app/navigation';

	interface Publication {
		id: number;
		name: string;
		start_date: string;
		end_date: string;
		application_only: boolean;
		collect_data: boolean;
		redirect_url: string;
		allow_anonymous: boolean;
	}

	interface Props {
		publications: Publication[];
		publicationFormData: SuperValidated<Infer<PublicationSchema>>;
	}

	let { publications, publicationFormData }: Props = $props();

	const form = superForm(publicationFormData, {
		validators: zodClient(publicationSchema),
		dataType: 'json',
		resetForm: true,
		onResult: (result) => {
			if (result.result.type === 'success') {
				open = false;
				invalidate('/projects');
			}
		}
	});

	const df = new DateFormatter('en-US', {
		dateStyle: 'long'
	});

	let open = $state(false);

	const { form: formData, enhance } = form;

	let startDateValue: DateValue | undefined = $derived(
		$formData.start_date ? parseDate($formData.start_date) : undefined
	);
	let endDateValue: DateValue | undefined = $derived(
		$formData.end_date ? parseDate($formData.end_date) : undefined
	);

	let placeholder: DateValue = $state(today(getLocalTimeZone()));

	const makeLink = (link_uuid: string) => {
		return `${$page.url.protocol}//${$page.url.host}/public/${link_uuid}`;
	};
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Publish</Card.Title>
		<Card.Description>Manage publishing of your survey or application.</Card.Description>
	</Card.Header>
	<Card.Content>
		{#if publications.length === 0}
			<p class="text-center text-muted-foregound">No publications found.</p>
		{:else}
			{#each publications as publication}
				<li class="border p-2 rounded">
					<strong>Name:</strong>
					{publication.name}<br />
					<strong>UUID:</strong>
					<a href={makeLink(publication.link_uuid)}>{makeLink(publication.link_uuid)}</a><br />
					<strong>Name:</strong>
					{publication.name}<br />
					<strong>Dates:</strong>
					{publication.start_date} - {publication.end_date}
				</li>
			{/each}
		{/if}
	</Card.Content>
	<Card.Footer>
		<Dialog.Root closeOnOutsideClick={false} bind:open>
			<Dialog.Trigger class={cn(buttonVariants({ variant: 'outline' }), 'w-full')}
				><CirclePlus class="mr-2 h-4 w-4" /> Add Publication</Dialog.Trigger
			>
			<Dialog.Content>
				<Dialog.Header>
					<Dialog.Title>Create a new publication.</Dialog.Title>
				</Dialog.Header>

				<form method="POST" use:enhance action="?/createPublication">
					<Form.Field {form} name="name">
						<Form.Control let:attrs>
							<Form.Label>Publication Name</Form.Label>
							<Input bind:value={$formData.name} {...attrs} placeholder="Publication Name" />
						</Form.Control>
						<Form.FieldErrors />
					</Form.Field>
					<Form.Field {form} name="start_date">
						<Form.Control let:attrs>
							<Form.Label>Start Date</Form.Label>
							<Popover.Root>
								<Popover.Trigger
									{...attrs}
									class={cn(
										buttonVariants({ variant: 'outline' }),
										'w-[280px] justify-start pl-4 text-left font-normal',
										!startDateValue && 'text-muted-foreground'
									)}
								>
									{startDateValue
										? df.format(startDateValue.toDate(getLocalTimeZone()))
										: 'Pick a start date'}
									<CalendarIcon class="ml-auto h-4 w-4 opacity-50" />
								</Popover.Trigger>
								<Popover.Content class="w-auto p-0" side="top">
									<Calendar
										value={startDateValue}
										bind:placeholder
										minValue={today(getLocalTimeZone())}
										calendarLabel="Start Date"
										initialFocus
										onValueChange={(v) => {
											if (v) {
												$formData.start_date = v.toString();
											} else {
												$formData.start_date = '';
											}
										}}
									/>
								</Popover.Content>
							</Popover.Root>
							<input type="hidden" value={$formData.start_date} name={attrs.name} />
						</Form.Control>
					</Form.Field>

					<Form.Field {form} name="end_date">
						<Form.Control let:attrs>
							<Form.Label>End Date</Form.Label>
							<Popover.Root>
								<Popover.Trigger
									{...attrs}
									class={cn(
										buttonVariants({ variant: 'outline' }),
										'w-[280px] justify-start pl-4 text-left font-normal',
										!endDateValue && 'text-muted-foreground'
									)}
								>
									{endDateValue
										? df.format(endDateValue.toDate(getLocalTimeZone()))
										: 'Pick an end date'}
									<CalendarIcon class="ml-auto h-4 w-4 opacity-50" />
								</Popover.Trigger>
								<Popover.Content class="w-auto p-0" side="top">
									<Calendar
										value={endDateValue}
										bind:placeholder
										minValue={today(getLocalTimeZone())}
										calendarLabel="End Date"
										initialFocus
										onValueChange={(v) => {
											if (v) {
												$formData.end_date = v.toString();
											} else {
												$formData.end_date = '';
											}
										}}
									/>
								</Popover.Content>
							</Popover.Root>
							<input type="hidden" value={$formData.end_date} name={attrs.name} />
						</Form.Control>
					</Form.Field>
					<Form.Field {form} name="application_only">
						<Form.Control let:attrs>
							<Form.Label>Application Only</Form.Label>
							<Checkbox bind:checked={$formData.application_only} {...attrs} />
						</Form.Control>
					</Form.Field>
					<Form.Field {form} name="collect_data">
						<Form.Control let:attrs>
							<Form.Label>Collect Data</Form.Label>
							<Checkbox bind:checked={$formData.collect_data} {...attrs} />
						</Form.Control>
					</Form.Field>
					<Form.Field {form} name="redirect_url">
						<Form.Control let:attrs>
							<Form.Label>Redirect URL</Form.Label>
							<Input bind:value={$formData.redirect_url} {...attrs} placeholder="Redirect URL" />
						</Form.Control>
						<Form.FieldErrors />
					</Form.Field>
					<Form.Field {form} name="allow_anonymous">
						<Form.Control let:attrs>
							<Form.Label>Allow Anonymous</Form.Label>
							<Checkbox bind:checked={$formData.allow_anonymous} {...attrs} />
						</Form.Control>
						<Form.FieldErrors />
					</Form.Field>

					<Dialog.Footer>
						<Form.Button>Save</Form.Button>
					</Dialog.Footer>
				</form>
			</Dialog.Content>
		</Dialog.Root>
	</Card.Footer>
</Card.Root>
