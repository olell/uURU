<script lang="ts">
	import {
		Button,
		Form,
		FormGroup,
		FormText,
		Icon,
		Input,
		Label,
		Modal,
		ModalBody
	} from '@sveltestrap/sveltestrap';
	import {
		createApiV1ExtensionPost,
		getMediaApiV1MediaGet,
		getPhoneTypesApiV1TelephoningTypesGet,
		type Media,
		updateApiV1ExtensionExtensionPatch,
		type Extension,
		type PhoneType
	} from '../client';
	import { push_api_error, push_message } from '../messageService.svelte';
	import { settings, user_info } from '../sharedState.svelte';
	import { Map, Marker, TileLayer } from 'sveaflet';
	import SchemaForm from '../components/schemaForm.svelte';
	import Ajv from 'ajv';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	const { extension }: { extension?: Extension } = $props();

	// inputs
	let selectedType = $state<PhoneType>();
	let extensionInput = $state(extension?.extension || '');
	let nameInput = $state(extension?.name || '');
	let infoInput = $state(extension?.info || '');
	let locationNameInput = $state(extension?.location_name || '');
	let publicInput = $state(!!extension ? extension.public : true);

	let phoneTypes = $state<PhoneType[]>([]);

	let showMap = $state(false);
	let map = $state<any>();
	let marker = $state<any>();
	let markerLat = $state<number | undefined>(extension?.lat / 10000000);
	let markerLon = $state<number | undefined>(extension?.lon / 10000000);

	$effect(() => {
		if (showMap) {
			map.invalidateSize();
			map.on('click', (e) => {
				markerLat = e.latlng.lat;
				markerLon = e.latlng.lng;
			});
		}
	});

	const toggleMap = () => {
		showMap = !showMap;
	};

	$effect(() => {
		getPhoneTypesApiV1TelephoningTypesGet({ credentials: 'include' }).then(({ data, error }) => {
			if (error) {
				push_api_error(error, 'Failed to load phone types!');
				return;
			}
			phoneTypes = data!.sort((a, b) => b.display_index - a.display_index);

			selectedType = !extension ? phoneTypes[0] : phoneTypes.find((t) => t.name == extension.type);
		});
	});

	let vanity_digits = {
		'2': ['a', 'b', 'c'],
		'3': ['d', 'e', 'f'],
		'4': ['g', 'h', 'i'],
		'5': ['j', 'k', 'l'],
		'6': ['m', 'n', 'o'],
		'7': ['p', 'q', 'r', 's'],
		'8': ['t', 'u', 'v'],
		'9': ['w', 'x', 'y', 'z']
	};

	$effect(() => {
		Object.keys(vanity_digits).forEach((d) => {
			vanity_digits[d].forEach((c: string) => {
				extensionInput = extensionInput.toLowerCase().replace(c, d);
			});
		});
	});

	const getLocation = () => {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(
				(pos) => {
					markerLat = pos.coords.latitude;
					markerLon = pos.coords.longitude;
				},
				(e) => {
					push_message({ color: 'danger', title: 'Error!', message: e.message });
				}
			);
		}
	};

	// extra data form and media assignments
	let extra_data = $state<any>(extension?.extra_fields || {});
	let assignedMedia = $state<Record<string, string>>({});
	$effect(() => {
		if (!selectedType || !selectedType.schema) {
			extra_data = {};
			assignedMedia = {};
			return;
		}
		// create empty extra_data object to bind form elements to
		let schema: any = selectedType.schema['properties'] as object;
		Object.keys(schema).forEach((element) => {
			extra_data[element] = extension?.extra_fields[element] || schema[element].default;
		});

		Object.keys(selectedType.media).forEach((name) => {
			assignedMedia[name] = extension?.media.find((m) => m.name == name)?.media_id || '';
		});
	});

	const handleSubmit = async (e: SubmitEvent) => {
		e.preventDefault();

		if (!selectedType) {
			push_message({
				color: 'danger',
				title: 'Error!',
				message: 'Failed to verify data since no phone type is selected!'
			});
			return;
		}

		if (user_info.val?.role !== 'admin') {
			// check if extension is reserved
			const reservation = settings.val?.RESERVED_EXTENSIONS.find((p) => {
				const ext = parseInt(extensionInput);
				return typeof p === 'number' ? p == ext : ext >= p[0] && ext <= p[1];
			});
			if (reservation) {
				push_message({
					color: 'danger',
					title: 'Extension reserved!',
					message: `Please use another extension, the \
						 ${typeof reservation == 'number' ? `extension ${reservation}` : `range ${reservation[0]}..${reservation[1]}`}\
						 is reserved! Or please ask an admin if you need to create this extension.`
				});
				return;
			}

			// check if name prefix is reserved
			const prefix = settings.val?.RESERVED_NAME_PREFIXES.find((p) =>
				nameInput.toLowerCase().trim().startsWith(p.trim().toLowerCase())
			);
			if (prefix) {
				push_message({
					color: 'danger',
					title: 'Name reserved!',
					message: `Please change the name, your extension name may not start with ${prefix}. Or please ask an admin if you need this prefix`
				});
				return;
			}
		}

		// validate extra data against schema
		if (selectedType.schema) {
			const ajv = new Ajv();
			const validator = ajv.compile(selectedType.schema);
			const is_valid = validator(extra_data);
			if (!is_valid && validator.errors) {
				for (const err of validator.errors) {
					let msg = '';
					switch (err.keyword) {
						case 'required':
							msg = `Missing required property: ${err.params.missingProperty}`;
						case 'type':
							msg = `Invalid type for ${err.propertyName || '(root)'}: expected ${err.params.type}`;
						case 'minLength':
							msg = `Too short: ${err.propertyName} should have at least ${err.params.limit} characters`;
						case 'minimum':
							msg = `Too small: ${err.propertyName} should be >= ${err.params.limit}`;
						case 'format':
							msg = `Invalid format for ${err.propertyName}: should be a valid ${err.params.format}`;
						case 'additionalProperties':
							msg = `Unexpected property: ${err.params.additionalProperty}`;
						default:
							msg = `${err.instancePath || '(root)'} ${err.message}`;
					}
					push_message({
						color: 'danger',
						title: 'Failed to validate!',
						message: msg
					});
				}
			}
		}

		// validate media
		let media_data: Record<string, string> = {};
		Object.keys(selectedType.media).forEach((name) => {
			const descr = selectedType!.media[name];
			let media_id = assignedMedia[name];
			if (descr.required && !media_id) {
				push_message({
					color: 'danger',
					title: 'Missing media!',
					message: `Missing ${name}`
				});
				return;
			}
			if (media_id || extension) {
				// || extension to include empty fields in update
				media_data[name] = media_id;
			}
		});

		const data = {
			type: selectedType.name,
			extension: extensionInput,
			name: nameInput,
			info: infoInput,
			location_name: locationNameInput,
			lat: markerLat,
			lon: markerLon,
			extra_fields: $state.snapshot(extra_data),
			public: publicInput,
			media: media_data
		};

		if (extension) {
			// update
			const { error } = await updateApiV1ExtensionExtensionPatch({
				credentials: 'include',
				body: data,
				path: { extension: extension.extension }
			});
			if (!!error) {
				push_api_error(error, 'Failed to update extension!');
				return;
			}
			push_message({ color: 'success', title: 'Saved!', message: 'Successfully stored changes!' });
		} else {
			// create
			const { error } = await createApiV1ExtensionPost({
				credentials: 'include',
				body: data
			});

			if (!!error) {
				push_api_error(error, 'Failed to create extension!');
				return;
			}
			push_message({
				color: 'success',
				title: 'Saved!',
				message: 'Successfully created extension!'
			});
		}

		console.log(data);
		goto(resolve('/extensions'));
	};

	let media = $state<Media[]>([]);

	$effect(() => {
		getMediaApiV1MediaGet({
			credentials: 'include',
			query: {
				all_media: false
			}
		}).then(({ data, error }) => {
			if (error) {
				push_api_error(error, 'Failed to retrieve media!');
				return;
			}
			media = data!;
		});
	});
</script>

<Form onsubmit={handleSubmit}>
	<FormGroup>
		<Label>Phone Type *</Label>
		<select class="form-select" disabled={!!extension} bind:value={selectedType} required>
			{#each phoneTypes as type (type.name)}
				<option value={type}>{type.name}</option>
			{/each}
		</select>
	</FormGroup>
	<FormGroup>
		<Label>Extension *</Label>
		<Input
			bind:value={extensionInput}
			minlength={settings.val?.EXTENSION_DIGITS}
			maxlength={settings.val?.EXTENSION_DIGITS}
			disabled={!!extension}
			required
		/>
		<FormText>
			The extension must be {settings.val?.EXTENSION_DIGITS} digits long. If you enter letters they will
			automatically be converted to their vanity digits.
		</FormText>
	</FormGroup>
	<FormGroup>
		<Label>Name *</Label>
		<Input
			bind:value={nameInput}
			placeholder="{user_info.val?.username}'s extension"
			maxlength={selectedType?.max_extension_name_chars}
			required
		/>
	</FormGroup>
	<FormGroup>
		<Label>Info</Label>
		<Input bind:value={infoInput} placeholder="..." />
		<FormText>
			You can store some information about this extension here. It will not be visible for the
			public.
		</FormText>
	</FormGroup>
	<FormGroup>
		<Label class="me-4">Location</Label>
		<a
			href={'#'}
			onclick={() => {
				showMap = true;
			}}><Icon name="pin-map-fill" class="me-2" />Select on map</a
		>
		<Input bind:value={locationNameInput} placeholder="{user_info.val?.username}'s base" />
	</FormGroup>

	<!-- Extra data -->
	{#if selectedType && selectedType.schema}
		<SchemaForm bind:value={extra_data} schema={selectedType.schema} />
	{/if}

	<FormGroup>
		<Input bind:checked={publicInput} type="switch" label="Show in public phonebook" />
	</FormGroup>

	{#if selectedType && Object.keys(selectedType.media).length > 0}
		<hr />
		<h1 class="fs-5">Media</h1>
		{#each Object.keys(selectedType.media) as key (key)}
			<FormGroup>
				<Label>{selectedType.media[key].label}{selectedType.media[key].required ? ' *' : ''}</Label>
				<select
					class="form-select"
					bind:value={assignedMedia[key]}
					required={selectedType.media[key].required}
				>
					{#if !selectedType.media[key].required}
						<option value="" selected={!assignedMedia[key]}>---</option>
					{/if}
					{#each media.filter((m) => m.type == selectedType!.media[key].media_type) as candidate (candidate.id)}
						<option value={candidate.id} selected={assignedMedia[key] == candidate.id}>
							{candidate.name}
						</option>
					{/each}
				</select>
			</FormGroup>
		{/each}
	{/if}

	<Button type="submit" color="primary" class="float-end ">{!!extension ? 'Save' : 'Create'}</Button
	>
</Form>

<Modal
	header="Select Location"
	class="modal-xl"
	centered
	isOpen={showMap}
	backdrop="static"
	toggle={toggleMap}
>
	<ModalBody>
		<div class="container" id="map-container">
			<Map
				options={{
					center: [settings.val?.SITE_LAT, settings.val?.SITE_LON],
					zoom: 15
				}}
				bind:instance={map}
			>
				<TileLayer url={'https://tile.openstreetmap.org/{z}/{x}/{y}.png'} />
				{#if markerLat && markerLon}
					<Marker
						latLng={[markerLat, markerLon]}
						bind:instance={marker}
						onclick={() => {
							markerLat = undefined;
							markerLon = undefined;
						}}
					></Marker>
				{/if}
			</Map>
		</div>
	</ModalBody>
	{#if navigator.geolocation}
		<Button onclick={getLocation} color="primary" class="m-4">Use GPS Location</Button>
	{/if}
</Modal>

<style>
	#map-container {
		height: 60vh;
	}
</style>
