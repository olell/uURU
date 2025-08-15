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
		deleteApiV1ExtensionExtensionDelete,
		type Extension,
		getOwnApiV1ExtensionOwnGet
	} from '../../client';
	import { push_api_error, push_message } from '../../messageService.svelte';
	import { isMobile } from '../../sharedState.svelte';

	let extensions = $state<Extension[]>([]);
	$inspect(extensions);

	$effect(() => {
		refreshExtensions();
	});

	async function refreshExtensions() {
		const { data, error } = await getOwnApiV1ExtensionOwnGet({ credentials: 'include' });
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

<h1 class="fs-3">Your Extensions</h1>
<hr />
{#if !isMobile.val}
	<Table striped>
		<thead>
			<tr>
				<th scope="col">#</th>
				<th scope="col">Name</th>
				<th scope="col">Type</th>
				<th scope="col">Visibility</th>
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
					<td>
						<a href={'#'} class="text-primary me-3"><Icon name="pencil-square" /></a>
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
			<ListGroupItem action>
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
						<a href={'#'} class="text-primary me-3 fs-3"><Icon name="pencil-square" /></a>
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
