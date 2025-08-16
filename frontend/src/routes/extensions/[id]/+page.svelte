<script lang="ts">
	import { page } from '$app/state';
	import { getApiV1ExtensionInfoExtensionGet, type Extension } from '../../../client';
	import { push_api_error } from '../../../messageService.svelte';
	import ExtensionEdit from '../../extension_edit.svelte';

	const { id } = page.params;
	let extension = $state<Extension>();

	$effect(() => {
		console.log(id);
		getApiV1ExtensionInfoExtensionGet({ credentials: 'include', path: { extension: id! } }).then(
			({ data, error }) => {
				if (error) {
					push_api_error(error, 'Failed to read extension data!');
					return;
				}

				extension = data!;
			}
		);
	});
</script>

{#if extension}
	<ExtensionEdit {extension} />
{/if}
