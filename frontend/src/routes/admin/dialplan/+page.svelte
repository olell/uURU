<script lang="ts">
	import { Button, Form, FormGroup, Icon, Input, Label, Modal, ModalBody, ModalFooter } from '@sveltestrap/sveltestrap';
	import {
		adminPhonebookApiV1ExtensionAllGet,
		type Extension,
		getDialplanExtensionsApiV1TelephoningDialplansGet,
		type Dialplan,
		getDialplanApiV1TelephoningDialplanExtenGet
	} from '../../../client';
	import { push_api_error } from '../../../messageService.svelte';
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

	let dialplan = $state<Dialplan>();

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
	const toggleNewDialplanModal = () => {showNewDialplanModal = !showNewDialplanModal};

	let newExtensionInput = $state("");
	let newExtensionValid = $derived(
		!!newExtensionInput && !knownDialplans.includes(newExtensionInput) && /^_?[0-9A-Za-z*#!]+$/.test(newExtensionInput)
	)

	const createDialplanFormSubmit = (e: Event) => {
		console.log("Create dialplan event")
		e.preventDefault();
		if (!newExtensionValid) return;

		selectedExtension = newExtensionInput;
		showNewDialplanModal = false;
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
					<a href={'#'} class="text-success me-3" onclick={toggleNewDialplanModal}><Icon name="plus-circle" /></a>
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
	
</div>
<hr>
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
				<Label>Extension (<a href="https://docs.asterisk.org/Confdtiguration/Dialplan/Pattern-Matching/" target="_blank">Format</a>)</Label>
				<Input type="text" bind:value={newExtensionInput}/>
			</FormGroup>
		</ModalBody>
		<ModalFooter>
				<Button type="submit" color="primary">Create</Button>
		</ModalFooter>
	</Form>
</Modal>