<script lang="ts">
	import {
		Badge,
		Form,
		FormGroup,
		Icon,
		Input,
		ListGroup,
		ListGroupItem
	} from '@sveltestrap/sveltestrap';
	import {
		adminPhonebookApiV1ExtensionAllGet,
		phonebookApiV1ExtensionPhonebookGet,
		type Extension,
		type ExtensionBase
	} from '../client';
	import { push_api_error, push_message } from '../messageService.svelte';
	import { isMobile, settings, user_info } from '../sharedState.svelte';
	import { Web } from 'sip.js';
	import Webphone from '../components/webphone.svelte';

	let query = $state('');

	let phonebook = $state<ExtensionBase[] | Extension[]>([]);

	let filtered_phonebook = $derived(
		phonebook.filter(
			(ext) => ext.name.toLowerCase().includes(query.toLowerCase()) || ext.extension.includes(query)
		)
	);

	$effect(() => {
		let handler:
			| typeof phonebookApiV1ExtensionPhonebookGet
			| typeof adminPhonebookApiV1ExtensionAllGet = phonebookApiV1ExtensionPhonebookGet;
		if (user_info.val?.role == 'admin') {
			handler = adminPhonebookApiV1ExtensionAllGet;
		}

		handler({ credentials: 'include' })
			.then(({ data, error }) => {
				if (error) {
					push_api_error(error, 'Failed to get phonebook data');
				}
				phonebook = data!;
			})
			.catch(() => {
				push_message({
					color: 'danger',
					title: 'Error!',
					message: 'Failed to get phonebook data!'
				});
			});
	});

	let showWebphone = $state(false);
	let webphoneTarget = $state<ExtensionBase | null>(null);

	const handleWebSIP = (target: ExtensionBase) => {
		if (settings.val?.ENABLE_WEBSIP) {
			showWebphone = true;
			webphoneTarget = target;
		} else {
			alert('Direct calling is disabled in this µURU instance!');
		}
	};
</script>

<Form class="row g-3">
	<FormGroup>
		<Input placeholder="Search extensions" bind:value={query} />
	</FormGroup>
</Form>

{#if !isMobile.val}
	<table class="table table-striped">
		<thead>
			<tr>
				<th scope="col">#</th>
				<th scope="col">Name</th>
				<th scope="col">Location</th>
				<th scope="col">Type</th>
				{#if user_info.val?.role == 'admin'}
					<th scope="col">Public</th>
					<th scope="col">Created By</th>
				{/if}
			</tr>
		</thead>
		<tbody>
			{#each filtered_phonebook as extension (extension.extension)}
				<tr>
					<td>
						<a href="#" onclick={() => handleWebSIP(extension)}>{extension.extension}</a>
					</td>
					<td>{extension.name}</td>
					<td>{extension.location_name || ''}</td>
					<td>{extension.type}</td>
					{#if user_info.val?.role == 'admin'}
						<td>{extension.public ? '' : 'Not Public'}</td>
						<td>{extension.created_by}</td>
					{/if}
				</tr>
			{/each}
		</tbody>
	</table>
{:else}
	<ListGroup>
		{#each filtered_phonebook as extension (extension.extension)}
			<ListGroupItem action on:click={() => handleWebSIP(extension)}>
				<div class="d-flex w-100 justify-content-between">
					<h5 class="mb-1">{extension.name}</h5>
					<p class="mb-1 fw-bold font-monospace">
						<Icon name="telephone-fill" />
						{extension.extension}
					</p>
				</div>
				<div class="d-flex w-100 justify-content-between mt-2">
					{#if extension.location_name}
						<Badge
							pill
							color="success"
							class="d-inline-flex align-items-center justify-content-start"
						>
							<Icon name="geo-alt-fill" class="me-2" />
							{extension.location_name}
						</Badge>
					{:else}<div></div>
					{/if}
					{extension.type}
				</div>
			</ListGroupItem>
		{/each}
	</ListGroup>
{/if}

{#if settings.val?.ENABLE_WEBSIP}
	<Webphone bind:isOpen={showWebphone} bind:target={webphoneTarget} />
{/if}
