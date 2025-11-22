<script lang="ts">
	import { Button, Icon, Modal, ModalBody } from '@sveltestrap/sveltestrap';
	import {
		createWebsipApiV1TelephoningWebsipGet,
		deleteWebsipApiV1TelephoningWebsipDelete,
		type WebSipExtension,
		type ExtensionBase,
		putWebsipApiV1TelephoningWebsipPut,
		getExtensionsOnlineApiV1ExtensionOnlineGet,
		type Extension,

		originateCallApiV1TelephoningOriginateGet

	} from '../client';
	import { Web } from 'sip.js';
	import { settings, user_info } from '../sharedState.svelte';
	import { push_api_error } from '../messageService.svelte';

	let { isOpen = $bindable<boolean>(), target = $bindable<ExtensionBase | null>() } = $props();

	let muted = $state(false);

	const close = async () => {
		if (user) {
			await handleHangup();
		}
		await teardown();
	};

	let callStarted = $state<Date | undefined>(undefined);
	let callTime = $state<string>('');

	$effect(() => {
		let interval = setInterval(() => {
			if (callStarted) {
				const now = new Date();
				const diff = Math.floor((now.getTime() - callStarted.getTime()) / 1000);
				const minutes = Math.floor(diff / 60)
					.toString()
					.padStart(2, '0');
				const seconds = (diff % 60).toString().padStart(2, '0');
				callTime = `${minutes}:${seconds}`;
			}
		}, 1000);
		return () => {
			clearInterval(interval);
		};
	});

	let status = $state<'prepare' | 'ring' | 'call' | 'teardown' | 'error'>('prepare');
	let statusText = $state('Start the call using the button below!');
	let statusColor = $state('info');
	$effect(() => {
		if (isOpen) {
			statusText = 'Start the call using the button below!';
			statusColor = 'info';

			if (user_info.val !== undefined) {
				refreshOnlineExtensions();
			}
		}
	});

	let onlineExtensions = $state<ExtensionBase[]>([]);
	let selectedSourceExtension = $state<string | null>(null);

	async function refreshOnlineExtensions() {
		let { data, error } = await getExtensionsOnlineApiV1ExtensionOnlineGet({
			credentials: 'include'
		});
		if (error) {
			push_api_error(error, 'Failed to load online extensions');
			return;
		}
		onlineExtensions = data!;
		if (data!.length > 0) {
			selectedSourceExtension = data![0].extension;
		}
	}

	// SimpleUser delegate
	const simpleUserDelegate: Web.SimpleUserDelegate = {
		onCallCreated: (): void => {
			console.log(`Call created`);
			statusText = 'Calling!';
			status = 'ring';
		},
		onCallAnswered: (): void => {
			console.log(`Call answered`);
			statusText = `Talking to ${target.name}`;
			callStarted = new Date();
			statusColor = 'success';
			status = 'call';
		},
		onCallHangup: (): void => {
			console.log(`Call hangup`);
			statusText = `Hungup!`;
			statusColor = 'danger';
			status = 'teardown';
			teardown();
		},
		onCallHold: (held: boolean): void => {
			console.log(`Call hold ${held}`);
			if (held) {
				statusText = 'Your call is on hold';
				statusColor = 'warning';
			} else {
				statusText = `Talking to ${target.name}`;
				statusColor = 'success';
			}
		}
	};

	let user = $state<Web.SimpleUser | undefined>(undefined);
	let extension = $state<WebSipExtension | undefined>(undefined);

	let refreshInterval = $state<ReturnType<typeof setInterval> | undefined>(undefined);

	const originateCall = async () => {
		if (!selectedSourceExtension) return;

		let result = await originateCallApiV1TelephoningOriginateGet({
			"credentials": "include",
			query: {
				source: selectedSourceExtension,
				dest: target.extension
			}
		});
		if (result.response.status == 204) {
			isOpen = false;
		}
	};

	const startCall = async () => {
		statusText = 'Creating temporary extension...';
		// create websip extension
		const { data, error } = await createWebsipApiV1TelephoningWebsipGet({ credentials: 'include' });
		if (error !== undefined || data === undefined) {
			statusText = 'Failed to create WebSIP extension for your call';
			statusColor = 'danger';
			return;
		}
		extension = data;
		statusText = `Created temporary extension ${extension.display_name} <${extension.extension}>`;

		// create interval to regulary refresh the extension
		refreshInterval = setInterval(() => {
			putWebsipApiV1TelephoningWebsipPut({
				credentials: 'include',
				query: { extension: extension!.extension }
			}).then(() => {
				console.log('Refreshed extension');
			});
		}, 60000);

		const options: Web.SimpleUserOptions = {
			aor: extension.aor,
			delegate: simpleUserDelegate,
			media: {
				remote: {
					audio: document.getElementById('websip-audio')
				}
			},
			userAgentOptions: {
				// logLevel: "debug",
				displayName: extension.display_name,
				authorizationUsername: extension.auth_user,
				authorizationPassword: extension.auth_pass
			}
		};

		user = new Web.SimpleUser(settings.val?.WEBSIP_WS_HOST!, options);
		statusText = 'Created SIP user';
		await user.connect();
		statusText = 'Connected... calling!';
		await user.call(`sip:${target.extension}@${settings.val?.ASTERISK_HOST!}`, {
			inviteWithoutSdp: false
		});
	};

	const handleHangup = async () => {
		await user?.hangup();
	};

	const toggleMute = async () => {
		muted = !muted;
		if (muted) user?.mute();
		else user?.unmute();
	};

	const teardown = async () => {
		clearInterval(refreshInterval);
		statusText = 'Cleaning up...';
		statusColor = 'danger';
		status = 'teardown';
		if (user) {
			await user.unregister();
		}
		if (extension) {
			await deleteWebsipApiV1TelephoningWebsipDelete({
				credentials: 'include',
				query: {
					extension: extension.extension,
					password: extension.auth_pass
				}
			});
		}
		statusText = 'Call ended!';
		user = undefined;
		extension = undefined;
		muted = false;
		target = undefined;
		status = 'prepare';
		callTime = '';
		callStarted = undefined;
		setTimeout(() => {
			isOpen = false;
		}, 1000);
	};
</script>

{#if target}
	<Modal
		centered
		backdrop="static"
		header="Call: {target.name} <{target.extension}>"
		{isOpen}
		toggle={close}
	>
		<ModalBody>
			<div class="d-flex justify-content-center text-{statusColor}">
				{statusText}
				{#if callTime}
					{callTime}
				{/if}
			</div>
			<div class="d-flex justify-content-center mt-3 gap-2">
				{#if user && (status == 'ring' || status == 'call')}
					<Button onclick={handleHangup} size="lg" color="danger"
						><Icon name="telephone-x-fill" /></Button
					>
				{/if}
				{#if status == 'prepare'}
					<Button onclick={startCall} size="lg" color="success"
						><Icon name="telephone-outbound-fill" /></Button
					>
				{/if}
				{#if status == 'call' || status == 'ring'}
					<Button onclick={toggleMute} size="lg" color="primary"
						><Icon name={muted ? 'mic-mute-fill' : 'mic-fill'} /></Button
					>
				{/if}
			</div>
			{#if user_info.val !== undefined && status == 'prepare'}
				<!-- check for any online extensions -->
				<hr />
				<div class="d-flex justify-content-center text-info">
					Send call to Phone
					<select class="form-select" bind:value={selectedSourceExtension}>
						{#each onlineExtensions as extension (extension.extension)}
							<option
								selected={extension.extension == selectedSourceExtension}
								value={extension.extension}>{extension.name} &lt;{extension.extension}&gt;</option
							>
						{/each}
					</select>
					<Button onclick={originateCall} class="ms-2" size="lg" color="info"
						><Icon name="telephone-forward-fill" /></Button
					>
				</div>
			{/if}
		</ModalBody>
	</Modal>

	<audio id="websip-audio"> </audio>
{/if}
