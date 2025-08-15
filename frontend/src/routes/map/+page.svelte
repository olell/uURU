<script lang="ts">
	import { Map, Marker, Popup, TileLayer } from 'sveaflet';
	import { settings, user_info } from '../../sharedState.svelte';
	import { phonebookApiV1ExtensionPhonebookGet, type ExtensionBase } from '../../client';
	import { push_api_error, push_message } from '../../messageService.svelte';

	let phonebook = $state<ExtensionBase[]>([]);

	$effect(() => {
		phonebookApiV1ExtensionPhonebookGet({
			credentials: 'include',
			query: { public: !(user_info.val?.role == 'admin') }
		})
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

<svelte:head>
	<link
		rel="stylesheet"
		href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
		integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
		crossorigin=""
	/>
	<script
		src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
		integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
		crossorigin=""
	></script>
</svelte:head>

<div class="container" id="map-container">
	<Map
		options={{
			center: [settings.val?.SITE_LAT, settings.val?.SITE_LON],
			zoom: 15
		}}
	>
		<TileLayer url={'https://tile.openstreetmap.org/{z}/{x}/{y}.png'} />
		{#each phonebook as extension (extension.extension)}
			{#if extension.lat && extension.lon}
				<Marker latLng={[extension.lat / 10000000.0, extension.lon / 10000000.0]}>
					<Popup
						options={{
							content: `<b>${extension.extension}</b><br/>${extension.name}<br/>${extension.location_name && '&rarr; '}${extension.location_name}`
						}}
					/>
				</Marker>
			{/if}
		{/each}
	</Map>
</div>

<style>
	#map-container {
		position: relative;
		height: 90vh; /* or as desired */
		width: 100%; /* This means "100% of the width of its container", the .col-md-8 */
	}
</style>
