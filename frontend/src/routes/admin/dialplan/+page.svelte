<script lang="ts">
	import {
		Button,
		Form,
		FormGroup,
		Icon,
		Input,
		Label,
		Modal,
		ModalBody,
		ModalFooter,
		Table
	} from '@sveltestrap/sveltestrap';
	import {
		adminPhonebookApiV1ExtensionAllGet,
		type BaseDialplanApp,
		type Dialplan,
		type Extension,
		getDialplanApiV1TelephoningDialplanExtenGet,
		getDialplanApplicationSchemasApiV1TelephoningDialplanSchemasGet,
		getDialplanExtensionsApiV1TelephoningDialplansGet,

		storeDialplanApiV1TelephoningDialplanStorePost
	} from '../../../client';
	import SchemaForm from '../../../components/schemaForm.svelte';
	import { push_api_error, push_message } from '../../../messageService.svelte';
	import { settings } from '../../../sharedState.svelte';

	let selectedExtension = $state<string>();

	/**
	 * Dialplan loading
	 */
	let knownDialplans = $state<string[]>([]);
	$effect(() => {
		getDialplanExtensionsApiV1TelephoningDialplansGet({ credentials: 'include' }).then(
			({ data, error }) => {
				if (error) {
					push_api_error(error, 'Failed to load existing dialplans!');
					return;
				}
				knownDialplans = data!;
			}
		);
	});

	let allExtensions = $state<Extension[]>([]);
	$effect(() => {
		adminPhonebookApiV1ExtensionAllGet({ credentials: 'include' })
			.then(({ data, error }) => {
				if (error) {
					push_api_error(error, 'Failed to get phonebook data!');
					return;
				}
				allExtensions = data!;
			})
			.catch(() => {
				push_message({
					color: 'danger',
					title: 'Error!',
					message: 'Failed to get phonebook data!'
				});
			});
	});

	type JSONSchema = {
		type?: string | string[];
		properties?: Record<string, JSONSchema>;
		items?: JSONSchema;
		default?: any;
		enum?: any[];
	};

	function generateFromSchema(schema: JSONSchema): any {
		if ('default' in schema) {
			return schema.default;
		}

		switch (schema.type) {
			case 'string':
				return '';
			case 'number':
			case 'integer':
				return 0;
			case 'boolean':
				return false;
			case 'array':
				if (schema.items) {
					return [generateFromSchema(schema.items)];
				}
				return [];
			case 'object':
				const obj: any = {};
				if (schema.properties) {
					for (const key in schema.properties) {
						obj[key] = generateFromSchema(schema.properties[key]);
					}
				}
				return obj;
			default:
				return null;
		}
	}

	let applicationSchemas = $state<Record<string, JSONSchema>>({});
	$inspect(applicationSchemas);

	$effect(() => {
		getDialplanApplicationSchemasApiV1TelephoningDialplanSchemasGet({ credentials: 'include' })
			.then(({ data, error }) => {
				if (error) {
					push_api_error(error, 'Failed to load application schemas!');
					return;
				}
				applicationSchemas = data!;
			})
			.catch(() => {
				push_message({
					color: 'danger',
					title: 'Error!',
					message: 'Failed to load application schemas!'
				});
			});
	});

	let dialplan = $state<Dialplan>();
	$inspect(dialplan);

	$effect(() => {
		if (selectedExtension) {
			getDialplanApiV1TelephoningDialplanExtenGet({
				credentials: 'include',
				path: { exten: selectedExtension }
			}).then(({ data, error }) => {
				if (error) {
					push_api_error(error, 'Failed to load dialplan!');
					return;
				}
				dialplan = data!;
				selectedEntry = undefined;
			});
		}
	});

	let isDialplanManaged = $derived<boolean>(
		!!allExtensions.find((e) => e.extension == selectedExtension) ||
			selectedExtension === `_${'X'.repeat(settings.val?.EXTENSION_DIGITS!)}`
	);

	/**
	 * Dialplan creation
	 */
	let showNewDialplanModal = $state(false);
	const toggleNewDialplanModal = () => {
		showNewDialplanModal = !showNewDialplanModal;
	};

	let newExtensionInput = $state('');
	let newExtensionValid = $derived(
		!!newExtensionInput &&
			!knownDialplans.includes(newExtensionInput) &&
			/^_?[0-9A-Za-z*#!]+$/.test(newExtensionInput)
	);

	const createDialplanFormSubmit = (e: Event) => {
		console.log('Create dialplan event');
		e.preventDefault();
		if (!newExtensionValid) return;

		selectedExtension = newExtensionInput;
		showNewDialplanModal = false;
	};

	let selectedEntry = $state<BaseDialplanApp | undefined>(undefined);
	let selectedSchema = $derived(
		!!selectedEntry &&
			Object.keys(applicationSchemas).includes(selectedEntry.app) &&
			applicationSchemas[selectedEntry.app]
	);

	const selectEntry = (prio: string) => {
		selectedEntry = dialplan?.entries![prio];
	};

	const moveEntryUp = (prio: string) => {
		const prios = Object.keys(dialplan?.entries!);
		const s = prios.sort();
		const idx = s.indexOf(prio);
		if (idx == prios.length - 1) return;

		const tmp = dialplan!.entries![prio];
		dialplan!.entries![prio] = dialplan!.entries![s[idx + 1]];
		dialplan!.entries![s[idx + 1]] = tmp;
		selectEntry(s[idx + 1]);
	};
	const moveEntryDown = (prio: string) => {
		const prios = Object.keys(dialplan?.entries!);
		const s = prios.sort();
		const idx = s.indexOf(prio);
		if (idx == 0) return;

		const tmp = dialplan!.entries![prio];
		dialplan!.entries![prio] = dialplan!.entries![s[idx - 1]];
		dialplan!.entries![s[idx - 1]] = tmp;
		selectEntry(s[idx - 1]);
	};

	let newEntry = $state<string | undefined>(undefined);
	const addEntry = () => {
		if (!newEntry || !Object.keys(applicationSchemas).includes(newEntry)) return;
		let schema = applicationSchemas[newEntry!];

		const prios = Object.keys(dialplan?.entries!);
		const s = prios.sort();
		const prio = (parseInt(s[prios.length - 1]) || 0) + 1;

		const data = generateFromSchema(schema);
		data['app'] = newEntry;
		dialplan.entries[prio.toString()] = data;

	};

	const removeEntry = (prio: string) => {
		delete dialplan.entries[prio];
		selectedEntry = undefined;
	};

	const storeDialplan = () => {
		storeDialplanApiV1TelephoningDialplanStorePost({credentials: "include", body: dialplan})
			.then(({data, error}) => {
				if (error) {
					push_api_error(error, 'Failed to save dialplan!');
					return;
				}
				dialplan = data!;
				selectedEntry = undefined;
				push_message({
					color: 'success',
					title: 'Saved!',
					message: 'Stored dialplan!'
				});
			})
			.catch(() => {
				push_message({
					color: 'danger',
					title: 'Error!',
					message: 'Failed to save dialplan!'
				});
			})
	}
</script>

<div class="row d-flex align-items-center">
	<div class="col col-md-6">
		<h2>Dialplan Editor</h2>
		{#if isDialplanManaged}
			<span class="text-danger text-decoration-underline">Attention:</span><br /><span>
				The selected dialplan belongs to an extension or is created by the system. Changing it may
				result in unexpected behavior and/or the dialplan will reset if the according extension is
				changed or the system restarts.
			</span>
			<span class="text-warning">So please be careful!</span>
		{/if}
	</div>
	<div class="col col-md-6">
		<Form onsubmit={createDialplanFormSubmit}>
			<FormGroup class="">
				<div class="me-3 mt-1">
					<Label>Load Dialplan</Label>
				</div>
				<div class="d-flex">
					<select class="form-select me-5" bind:value={selectedExtension}>
						{#if selectedExtension && !knownDialplans.includes(selectedExtension)}
							<option value={selectedExtension} selected>{selectedExtension}</option>
						{/if}
						{#each knownDialplans as plan (plan)}
							<option value={plan}>{plan}</option>
						{/each}
					</select>
					<a href={'#'} class="text-success me-3" onclick={toggleNewDialplanModal}
						><Icon name="plus-circle" /></a
					>
					{#if selectedExtension && !isDialplanManaged}
						<a href={'#'} class="text-danger me-3" onclick={() => {}}><Icon name="trash3" /></a>
					{/if}
				</div>
			</FormGroup>
		</Form>
	</div>
</div>
<hr />

{#if !dialplan}
	<div class="row">
		<div>No dialplan available, please load or create a new one!</div>
	</div>
{:else}
	<div class="row">
		<div class="col col-md-4">
			<h4>Entries</h4>
			<Table class="table table-striped action">
				<tbody>
					{#each Object.keys(dialplan.entries!) as prio, index (prio)}
						<tr>
							<td>{prio}</td>
							<td title={dialplan.entries![prio].assembled}>{dialplan.entries![prio].app}</td>
							<td>
								{#if index > 0}
									<a href={'#'} class="text-success" onclick={() => moveEntryDown(prio)}
										><Icon name="chevron-up" /></a
									>
								{/if}
							</td>
							<td>
								{#if index < Object.keys(dialplan.entries!).length - 1}
									<a href={'#'} class="text-success" onclick={() => moveEntryUp(prio)}
										><Icon name="chevron-down" /></a
									>
								{/if}
							</td>
							<td>
								<a href={'#'} class="text-info ms-3" onclick={() => selectEntry(prio)}
									><Icon name="pencil" /></a
								>
								<a href={'#'} class="text-danger ms-3" onclick={() => removeEntry(prio)}
									><Icon name="trash3" /></a
								>
							</td>
						</tr>
					{/each}
					<tr>
						<td
							><a href={'#'} class="text-success" onclick={addEntry}><Icon name="plus-circle" /></a
							></td
						>
						<td>
							<select class="form-select" bind:value={newEntry}>
								{#each Object.keys(applicationSchemas) as application (application)}
									<option value={application} selected={application == newEntry}
										>{application}</option
									>
								{/each}
							</select>
						</td>
						<td></td>
						<td></td>
						<td></td>
					</tr>
				</tbody>
			</Table>
			<Button color="success" onclick={storeDialplan}>Apply</Button>
		</div>
		<div class="col">
			{#if selectedEntry && selectedSchema}
				<h4>Edit {selectedEntry.app}</h4>
				<SchemaForm bind:value={selectedEntry} schema={selectedSchema}></SchemaForm>
			{/if}
		</div>
	</div>
	<hr />
	<div class="row">
		<h4>Current asterisk configuration</h4>
		<pre>
{dialplan.asterisk_config}
	</pre>
	</div>
{/if}

<Modal header="New Dialplan" isOpen={showNewDialplanModal} toggle={toggleNewDialplanModal} centered>
	<Form validated={newExtensionValid} onsubmit={createDialplanFormSubmit}>
		<ModalBody>
			<FormGroup>
				<Label
					>Extension (<a
						href="https://docs.asterisk.org/Confdtiguration/Dialplan/Pattern-Matching/"
						target="_blank">Format</a
					>)</Label
				>
				<Input type="text" bind:value={newExtensionInput} />
			</FormGroup>
		</ModalBody>
		<ModalFooter>
			<Button type="submit" color="primary">Create</Button>
		</ModalFooter>
	</Form>
</Modal>
