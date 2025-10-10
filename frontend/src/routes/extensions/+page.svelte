<script lang="ts">
	import {
		Badge,
		Button,
		Icon,
		ListGroup,
		ListGroupItem,
		Popover,
		Table
	} from '@sveltestrap/sveltestrap';
	import {
		adminPhonebookApiV1ExtensionAllGet,
		deleteApiV1ExtensionExtensionDelete,
		type Extension,
		getOwnApiV1ExtensionOwnGet
	} from '../../client';
	import { push_api_error, push_message } from '../../messageService.svelte';
	import { adminMode, isMobile } from '../../sharedState.svelte';
	import { resolve } from '$app/paths';

	let extensions = $state<Extension[]>([]);

	$effect(() => {
		refreshExtensions();
	});

	async function refreshExtensions() {
		let handler = adminMode.val ? adminPhonebookApiV1ExtensionAllGet : getOwnApiV1ExtensionOwnGet;
		const { data, error } = await handler({ credentials: 'include' });
		if (error) {
			push_api_error(error, 'Failed to load extensions');
			return;
		}
		extensions = data!;
	}

	async function deleteExtension(extension: Extension) {
		const { data, error } = await deleteApiV1ExtensionExtensionDelete({
			credentials: 'include',
			path: { extension: extension.extension }
		});

		if (error) {
			push_api_error(error, 'Failed to delete extension');
			return;
		}

		push_message({
			color: 'success',
			title: 'Deleted!',
			message: `Delted Extension ${extension.name} <${extension.extension}>`
		});
		refreshExtensions();
	}
</script>

<h1 class="fs-3">{adminMode.val ? 'All' : 'Your'} Extensions</h1>
<hr />
{#if !isMobile.val}
	<Table striped>
		<thead>
			<tr>
				<th scope="col">#</th>
				<th scope="col">Name</th>
				<th scope="col">Type</th>
				<th scope="col">Visibility</th>
				{#if adminMode.val}
					<th scope="col">Created By</th>
				{/if}
				<th scope="col">Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each extensions as extension (extension.extension)}
				<tr>
					<td>{extension.extension}</td>
					<td>{extension.name}</td>
					<td>{extension.type}</td>
					<td>{extension.public ? '' : 'Not Public'}</td>
					{#if adminMode.val}
						<td>{extension.created_by}</td>
					{/if}
					<td>
						<a
							href={resolve(`/extensions/edit?extension=${extension.extension}`)}
							class="text-primary me-3"><Icon name="pencil-square" /></a
						>
						<a
							href={'#'}
							class="text-danger me-3"
							onclick={() => {
								deleteExtension(extension);
							}}><Icon name="trash3" /></a
						>
						<a href={'#'} id="popover-trigger-{extension.extension}" class="text-warning"
							><Icon name="key-fill" /></a
						>
						<Popover
							trigger="click"
							placement="auto"
							target="popover-trigger-{extension.extension}"
						>
							<b>Password:</b><br />
							{extension.password}<br /><br /><b>Token:</b><br />
							{extension.token}
						</Popover>
					</td>
				</tr>
			{/each}
		</tbody>
	</Table>
{:else}
	<ListGroup>
		{#each extensions as extension (extension.extension)}
			<ListGroupItem action href={resolve(`/extensions/edit?extension=${extension.extension}`)}>
				<div class="d-flex w-100 justify-content-between">
					<h5 class="mb-1">{extension.name}</h5>

					<p class="mb-1 fw-bold font-monospace">
						<Icon name="motherboard" />
						{extension.type}
						<Icon name="telephone-fill" />
						{extension.extension}
					</p>
				</div>
				<div class="d-flex w-100 justify-content-between mt-2">
					<div>
						{#if adminMode.val}
							<Badge
								pill
								color="primary"
								class="d-inline-flex align-items-center justify-content-start"
							>
								<Icon name="person-fill" class="me-2" />{extension.created_by}
							</Badge>
						{/if}
						{#if extension.location_name}
							<Badge
								pill
								color="success"
								class="d-inline-flex align-items-center justify-content-start"
							>
								<Icon name="geo-alt-fill" class="me-2" />
								{extension.location_name}
							</Badge>
						{/if}
						{#if !extension.public}
							<Badge
								pill
								color="secondary"
								class="d-inline-flex align-items-center justify-content-start"
							>
								<Icon name="eye-slash-fill" class="me-2" /> Not Public
							</Badge>
						{/if}
					</div>
					<div>
						<a
							href={resolve(`/extensions/edit?extension=${extension.extension}`)}
							class="text-primary me-3 fs-3"><Icon name="pencil-square" /></a
						>
						<a
							href={'#'}
							class="text-danger me-3 fs-3"
							onclick={() => {
								deleteExtension(extension);
							}}><Icon name="trash3" /></a
						>
						<a href={'#'} id="popover-trigger-{extension.extension}" class="text-warning fs-3"
							><Icon name="key-fill" /></a
						>
						<Popover
							trigger="click"
							placement="auto"
							target="popover-trigger-{extension.extension}"
						>
							<b>Password:</b><br />
							{extension.password}<br /><br /><b>Token:</b><br />
							{extension.token}
						</Popover>
					</div>
				</div>
			</ListGroupItem>
		{/each}
	</ListGroup>
{/if}
