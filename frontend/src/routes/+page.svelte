<script lang="ts">
	import {
		adminPhonebookApiV1ExtensionPhonebookAdminGet,
		phonebookApiV1ExtensionPhonebookGet,
		type Extension,
		type ExtensionBase
	} from '../client';
	import { push_api_error, push_message } from '../messageService.svelte';
	import { user_info } from '../sharedState.svelte';

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
			| typeof adminPhonebookApiV1ExtensionPhonebookAdminGet = phonebookApiV1ExtensionPhonebookGet;
		if (user_info.val?.role == 'admin') {
			handler = adminPhonebookApiV1ExtensionPhonebookAdminGet;
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
</script>

<form class="row g-3">
	<div class="col-10">
		<input type="text" class="form-control" name="query" bind:value={query} />
	</div>
	<div class="col-2">
		<button type="submit" class="btn btn-primary">Search</button>
	</div>
</form>

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
					<a href="tel:{extension.extension}">{extension.extension}</a>
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
