<script lang="ts">
	import {
		Button,
		Container,
		Form,
		FormCheck,
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
		getMediaApiV1MediaGet,
		type MediaType,
		type Media,
		createMediaApiV1MediaPost,
		deleteMediaApiV1MediaMediaIdDelete
	} from '../../client';
	import { settings, user_info } from '../../sharedState.svelte';
	import { push_api_error } from '../../messageService.svelte';
	import { client } from '../../client/client.gen';

	let imageOpen = $state(false);
	let selectedImage = $state<Media>();
	const toggleImageOpen = () => {
		imageOpen = !imageOpen;
	};

	let showUploadModal = $state(false);
	const toggleShowUploadModal = () => {
		showUploadModal = !showUploadModal;
	};

	let uploadName = $state('');
	let uploadType = $state<MediaType>('raw');
	let upload = $state<FileList>();

	$effect(() => {
		if (upload && upload.length == 1) {
			if (upload[0].type.startsWith('image')) {
				uploadType = 'image';
			} else if (upload[0].type.startsWith('audio')) {
				uploadType = 'audio';
			} else {
				uploadType = 'raw';
			}
			console.log(uploadType);
		} else {
			console.log(upload);
		}
	});

	let adminMode = $state(false);

	let media = $state<Media[]>([]);
	$inspect(media);
	let audios = $derived(media.filter((e) => e.type === 'audio'));
	let images = $derived(media.filter((e) => e.type === 'image'));
	let raws = $derived(media.filter((e) => e.type === 'raw'));
	const updateMedia = () => {
		console.log('updated media');
		getMediaApiV1MediaGet({
			credentials: 'include',
			query: { all_media: adminMode }
		}).then(({ data, error }) => {
			if (error) {
				push_api_error(error, 'Failed to load media!');
				return;
			}
			media = data!;
		});
	};
	$effect(updateMedia);

	const createMedia = (event: Event) => {
		event.preventDefault();
		createMediaApiV1MediaPost({
			credentials: 'include',
			query: {
				name: uploadName,
				supposed_type: uploadType
			},
			body: {
				file: upload![0]
			}
		})
			.then(({ data, error }) => {
				if (error) {
					push_api_error(error, 'Failed to upload media');
					return;
				}
				updateMedia();
				uploadName = '';
				uploadType = 'raw';
				upload = undefined;
				showUploadModal = false;
			})
			.catch(({ error }) => {
				push_api_error(error, 'Failed to upload media');
			});
	};

	const deleteMedia = (media: Media) => {
		deleteMediaApiV1MediaMediaIdDelete({
			credentials: 'include',
			path: { media_id: media.id! }
		}).then(({ data, error }) => {
			if (error) {
				push_api_error(error, 'Failed to delete media!');
				return;
			}
			updateMedia();
		});
	};
</script>

<h1 class="fs-3">Media</h1>

{#if user_info.val?.role == 'admin'}
	<div class="form-check form-switch">
		<input
			class="form-check-input"
			type="checkbox"
			role="switch"
			bind:checked={adminMode}
			id="example-switch-1"
		/>
		<label class="form-check-label" for="example-switch-1">
			Admin Mode (show media from all users)
		</label>
	</div>
{/if}
<Button
	color="primary"
	class="mt-3"
	onclick={() => {
		showUploadModal = true;
	}}>Upload New</Button
>

<h1 class="fs-4 mt-4">Your Media</h1>

<hr />
<h1 class="fs-5">Audio Files</h1>
{#if audios.length > 0}
	<Table striped>
		<thead>
			<tr>
				<th class="col-md-2" scope="col">Name</th>
				<th class="col-md-8" scope="col">Media</th>
				<th class="col-md-2" scope="col">Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each audios as audio (audio.id)}
				<tr>
					<td>{audio.name}</td>
					<td>
						<audio controls class="w-100">
							<source src="{client.getConfig().baseUrl}/api/v1/media/byid/{audio.stored_as}" />
						</audio>
					</td>
					<td>
						<a href={'#'} onclick={() => deleteMedia(audio)} class="text-danger">
							<Icon name="trash3"></Icon>
						</a>
					</td>
				</tr>
			{/each}
		</tbody>
	</Table>
{:else}
	No Audio Files
{/if}

<hr />
<h1 class="fs-5">Raw files</h1>
{#if raws.length > 0}
	<Table striped>
		<thead>
			<tr>
				<th class="col-md-10" scope="col">Name</th>
				<th class="col-md-2" scope="col">Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each raws as raw (raw.id)}
				<tr>
					<td>{raw.name}</td>
					<td>
						<a href={'#'} onclick={() => deleteMedia(raw)} class="text-danger">
							<Icon name="trash3"></Icon>
						</a>
					</td>
				</tr>
			{/each}
		</tbody>
	</Table>{:else}
	No Raw Files
{/if}

<hr />
<h1 class="fs-5">Image Gallery</h1>
{#if images.length > 0}
	<Container class="display-flex">
		{#each images as image (image.id)}
			<a
				href={'#'}
				onclick={() => {
					selectedImage = image;
					imageOpen = true;
				}}
			>
				<img
					class="rounded img-thumbnail gallery-image"
					alt={image.name}
					src="{client.getConfig().baseUrl}/api/v1/media/byid/{image.stored_as}"
				/>
			</a>
		{/each}
	</Container>
{:else}
	No Images
{/if}

<Modal
	centered
	class="modal-dialog modal-lg"
	header="Upload New"
	isOpen={showUploadModal}
	toggle={toggleShowUploadModal}
>
	<Form onsubmit={createMedia}>
		<ModalBody>
			<FormGroup>
				<Label>Name</Label>
				<Input bind:value={uploadName} required />
			</FormGroup>
			<FormGroup>
				<Label>Media Type</Label>
				<select class="form-select" bind:value={uploadType} required>
					<option value="image">Image</option>
					<option value="audio">Audio</option>
					<option value="raw">Raw</option>
				</select>
			</FormGroup>
			<FormGroup>
				<Label>File</Label>
				<Input type="file" bind:files={upload} required />
			</FormGroup>
		</ModalBody>
		<ModalFooter>
			<Input type="submit" value="Upload!" color="primary" />
		</ModalFooter>
	</Form>
</Modal>

<Modal
	centered
	class="modal-dialog modal-xl"
	header={selectedImage?.name}
	isOpen={imageOpen}
	toggle={toggleImageOpen}
>
	<img
		style="max-width: 100%"
		alt={selectedImage!.name}
		src="{client.getConfig().baseUrl}/api/v1/media/byid/{selectedImage!.stored_as}"
	/>
	<ModalFooter>
		<Button
			onclick={() => {
				deleteMedia(selectedImage!);
				imageOpen = false;
			}}
			color="danger">Delete</Button
		>
	</ModalFooter>
</Modal>

<style>
	.gallery-image {
		max-width: 280px;
		max-height: 280px;
	}
</style>
