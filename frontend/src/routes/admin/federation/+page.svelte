<script lang="ts">
	import {
		Button,
		Col,
		Container,
		Form,
		FormGroup,
		FormText,
		Icon,
		Input,
		Label,
		Modal,
		ModalBody,
		ModalFooter,
		Row,
		Table
	} from '@sveltestrap/sveltestrap';
	import {
		createOutgoingPeeringRequestApiV1FederationOutgoingRequestPost,
		getIncomingPeeringRequestsApiV1FederationIncomingRequestsGet,
		getOutgoingPeeringRequestsApiV1FederationOutgoingRequestsGet,
		type IncomingPeeringRequestBase,
		revokeOutgoingPeeringRequestApiV1FederationOutgoingRequestDelete,
		type OutgoingPeeringRequestPublic,
		type IncomingRequestStatus,
		setIncomingPeeringRequestStatusApiV1FederationIncomingRequestRequestIdPut,
		type PeerBase,
		getPeersApiV1FederationPeersGet,
		deletePeerApiV1FederationPeerPeerIdDelete
	} from '../../../client';
	import { push_api_error } from '../../../messageService.svelte';

	let newRequestOpen = $state(false);
	const newRequestToggle = () => {
		newRequestOpen = !newRequestOpen;
	};

	let requestHost = $state('');
	let requestPrefix = $state('');
	let requestName = $state('');
	let requestCodec = $state<'g722' | 'alaw' | 'ulaw' | 'g726' | 'gsm' | 'lpc10'>('g722');

	const codecLabel: Record<string, string> = {
		g722: 'G.722',
		alaw: 'G.711 A-law',
		ulaw: 'G.711 µ-law',
		g726: 'G.726',
		gsm: 'GSM',
		lpc10: 'FIPS 137 / LPC-10'
	};

	let repeatLocalModalOpen = $state(false);
	let repeatLocalModalText = $state('');
	let repeatLocalModalCallback = $state(() => {});
	const resetRepeatLocalModal = () => {
		repeatLocalModalOpen = false;
		repeatLocalModalText = '';
		repeatLocalModalCallback = () => {};
	};

	const sendRequest = async (e: Event) => {
		e.preventDefault();
		const { data, error } = await createOutgoingPeeringRequestApiV1FederationOutgoingRequestPost({
			credentials: 'include',
			body: {
				name: requestName,
				prefix: requestPrefix,
				partner_uuru_host: requestHost,
				codec: requestCodec
			}
		});
		if (!!error) {
			push_api_error(error, 'Failed to create outgoing peering request!');
		}
		requestHost = '';
		requestPrefix = '';
		requestName = '';
		requestCodec = 'g722';
		newRequestOpen = false;
		updateOutgoingRequests();
	};

	let outgoingRequests = $state<OutgoingPeeringRequestPublic[]>([]);
	const updateOutgoingRequests = () => {
		getOutgoingPeeringRequestsApiV1FederationOutgoingRequestsGet({
			credentials: 'include'
		})
			.then((response) => {
				outgoingRequests = response.data!;
			})
			.catch((error) => {
				push_api_error(error, 'Failed to retrieve outgoing peering requests!');
			});
	};
	$effect(() => {
		let interval = setInterval(() => {
			updateOutgoingRequests();
		}, 30000);
		updateOutgoingRequests();
		return () => {
			clearInterval(interval);
		};
	});

	const revokeRequest = async (request: OutgoingPeeringRequestPublic) => {
		revokeOutgoingPeeringRequestApiV1FederationOutgoingRequestDelete({
			credentials: 'include',
			query: {
				request_id: request.id!,
				local_only: repeatLocalModalOpen
			}
		})
			.then(({ data, error }) => {
				if (!error) {
					updateOutgoingRequests();
					resetRepeatLocalModal();
				} else {
					if (repeatLocalModalOpen) {
						// failed second time, show error
						push_api_error(error, 'Failed to revoke request!');
						resetRepeatLocalModal();
					} else {
						// failed first time, open repeat modal
						repeatLocalModalOpen = true;
						repeatLocalModalText = error.detail;
						repeatLocalModalCallback = () => {
							revokeRequest(request);
						};
					}
				}
			})
			.catch(({ error }) => {
				push_api_error(error, 'Failed revoking outgoing peering request!');
			});
	};

	let incomingRequests = $state<IncomingPeeringRequestBase[]>([]);
	const updateIncomingRequests = () => {
		getIncomingPeeringRequestsApiV1FederationIncomingRequestsGet({
			credentials: 'include'
		})
			.then((response) => {
				incomingRequests = response.data!;
			})
			.catch(({ error }) => {
				push_api_error(error, 'Failed to retrieve incoming peering requests!');
			});
	};
	$effect(() => {
		let interval = setInterval(() => {
			updateIncomingRequests();
		}, 30000);
		updateIncomingRequests();
		return () => {
			clearInterval(interval);
		};
	});

	const setIncomingRequestState = async (
		request: IncomingPeeringRequestBase,
		status: IncomingRequestStatus
	) => {
		status.local_only = repeatLocalModalOpen && !status.accept;
		setIncomingPeeringRequestStatusApiV1FederationIncomingRequestRequestIdPut({
			credentials: 'include',
			path: {
				request_id: request.id!
			},
			body: status
		})
			.then(({ data, error }) => {
				if (!error) {
					updateIncomingRequests();
					updatePeers();
					resetRepeatLocalModal();
				} else {
					if (status.accept == true || repeatLocalModalOpen) {
						push_api_error(error, 'Failed to set incoming request status!');
						resetRepeatLocalModal();
					} else {
						repeatLocalModalOpen = true;
						repeatLocalModalText = error.detail;
						repeatLocalModalCallback = () => {
							setIncomingRequestState(request, status);
						};
					}
				}
			})
			.catch(({ error }) => {
				push_api_error(error, 'Failed to set incoming request state!');
			});
	};

	let acceptModalOpen = $state(false);
	let acceptModalToggle = () => {
		acceptModalOpen = !acceptModalOpen;
	};
	let acceptModalRequest = $state<IncomingPeeringRequestBase | undefined>(undefined);
	let acceptModalPrefixInput = $state('');

	const acceptIncomingRequest = (event: Event) => {
		event.preventDefault();

		if (!acceptModalRequest) return;

		setIncomingRequestState(acceptModalRequest, {
			accept: true,
			prefix: acceptModalPrefixInput
		});

		acceptModalOpen = false;
		acceptModalRequest = undefined;
		acceptModalPrefixInput = '';
	};
	const declineIncomingRequest = async (request: IncomingPeeringRequestBase) => {
		setIncomingRequestState(request, {
			accept: false
		});
	};

	let peers = $state<PeerBase[]>([]);
	const updatePeers = () => {
		getPeersApiV1FederationPeersGet({
			credentials: 'include'
		})
			.then(({ data }) => {
				peers = data!;
			})
			.catch(({ error }) => {
				push_api_error(error, 'Failed to retrieve peers!');
			});
	};

	$effect(() => {
		let interval = setInterval(() => {
			updatePeers();
		}, 30000);
		updatePeers();
		return () => {
			clearInterval(interval);
		};
	});

	const teardownPeering = async (peer: PeerBase) => {
		deletePeerApiV1FederationPeerPeerIdDelete({
			credentials: 'include',
			path: { peer_id: peer.id! },
			query: {
				local_only: repeatLocalModalOpen
			}
		})
			.then(({ data, error }) => {
				if (!error) {
					updatePeers();
					resetRepeatLocalModal();
				} else {
					if (repeatLocalModalOpen) {
						push_api_error(error, 'Failed to teardown peer!');
						resetRepeatLocalModal();
					} else {
						repeatLocalModalOpen = true;
						repeatLocalModalText = error.detail;
						repeatLocalModalCallback = () => {
							teardownPeering(peer);
						};
					}
				}
			})
			.catch(({ error }) => {
				push_api_error(error, 'Failed to teardown peering!');
			});
	};
</script>

<h2>Federation</h2>
<hr />

<h3>
	Peers
	<Button
		size="lg"
		color="link"
		onclick={() => {
			updatePeers();
			updateOutgoingRequests();
		}}
	>
		<Icon name="arrow-clockwise"></Icon>
	</Button>
</h3>
<Table striped>
	<thead>
		<tr>
			<th scope="col">Name</th>
			<th scope="col">Prefix</th>
			<th scope="col">Partner</th>
			<th scope="col">Partner Ext.-Length</th>
			<th scope="col">Codec</th>
			<th scope="col">Actions</th>
		</tr>
	</thead>
	<tbody>
		{#each peers as peer (peer.id)}
			<tr>
				<td>{peer.name}</td>
				<td>{peer.prefix}</td>
				<td>
					<a target="_blank" rel="noopener noreferrer" href={peer.partner_uuru_host}>
						{peer.partner_uuru_host}
					</a>
				</td>
				<td>{peer.partner_extension_length}</td>
				<td>{codecLabel[peer.codec!]}</td>
				<td>
					<a href={'#'} onclick={() => teardownPeering(peer)} class="text-danger">
						<Icon name="trash3"></Icon>
					</a>
				</td>
			</tr>
		{/each}
	</tbody>
</Table>

<hr />
<Container>
	<Row>
		<Col>
			<h4>
				Outgoing Peering Requests
				<Button size="lg" color="link" onclick={() => (newRequestOpen = true)}>
					<Icon name="plus-circle"></Icon>
				</Button>
			</h4>
			<Table striped>
				<thead>
					<tr>
						<th scope="col">Name</th>
						<th scope="col">Prefix</th>
						<th scope="col">Codec</th>
						<th scope="col">Host</th>
						<th scope="col">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each outgoingRequests as request (request.id)}
						<tr>
							<td>{request.name}</td>
							<td>{request.prefix}</td>
							<td>{codecLabel[request.codec!]}</td>
							<td>
								<a target="_blank" rel="noopener noreferrer" href={request.partner_uuru_host}>
									{request.partner_uuru_host}
								</a>
							</td>
							<td>
								<a href={'#'} onclick={() => revokeRequest(request)} class="text-danger">
									<Icon name="trash3"></Icon>
								</a>
							</td>
						</tr>
					{/each}
				</tbody>
			</Table>
		</Col>
		<Col>
			<h4>
				Incoming Peering Requests
				<Button size="lg" color="link" onclick={updateIncomingRequests}>
					<Icon name="arrow-clockwise"></Icon>
				</Button>
			</h4>
			<Table striped>
				<thead>
					<tr>
						<th scope="col">Name</th>
						<th scope="col">Origin</th>
						<th scope="col">Origin Ext.-Length</th>
						<th scope="col">Codec</th>
						<th scope="col">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each incomingRequests as request (request.id)}
						<tr>
							<td>{request.name}</td>
							<td>
								<a target="_blank" rel="noopener noreferrer" href={request.partner_uuru_host}>
									{request.partner_uuru_host}
								</a>
							</td>
							<td>{request.partner_extension_length}</td>
							<td>{codecLabel[request.codec!]}</td>
							<td>
								<a
									href={'#'}
									onclick={() => {
										acceptModalOpen = true;
										acceptModalRequest = request;
									}}
									class="text-success"
								>
									<Icon name="check-lg"></Icon>
								</a>
								<a href={'#'} onclick={() => declineIncomingRequest(request)} class="text-danger">
									<Icon name="x-lg"></Icon>
								</a>
							</td>
						</tr>
					{/each}
				</tbody>
			</Table>
		</Col>
	</Row>
</Container>

<Modal
	centered
	header="Create a new Peering Request"
	isOpen={newRequestOpen}
	toggle={newRequestToggle}
>
	<ModalBody>
		<Form onsubmit={sendRequest}>
			<FormGroup>
				<Label>Name</Label>
				<Input bind:value={requestName} required />
			</FormGroup>
			<FormGroup>
				<Label>Host</Label>
				<Input pattern="https?:\/\/.*" bind:value={requestHost} required />
				<FormText>Please include the protocol (http:// or https://)</FormText>
			</FormGroup>
			<FormGroup>
				<Label>Prefix</Label>
				<Input pattern="\d+" bind:value={requestPrefix} required />
			</FormGroup>
			<FormGroup>
				<Label>Codec</Label>
				<select class="form-select" bind:value={requestCodec} required>
					{#each Object.keys(codecLabel) as codec (codec)}
						<option value={codec}>{codecLabel[codec]}</option>
					{/each}
				</select>
			</FormGroup>
			<Input type="submit" value="Send" />
		</Form>
	</ModalBody>
</Modal>

<Modal
	centered
	backdrop="static"
	header="Accept Peering Request"
	isOpen={acceptModalOpen}
	toggle={acceptModalToggle}
>
	<ModalBody>
		<Form onsubmit={acceptIncomingRequest}>
			<FormGroup>
				<Label>Prefix</Label>
				<Input pattern="\d+" bind:value={acceptModalPrefixInput} required />
			</FormGroup>
			<Input type="submit" color="success" value="Accept" />
		</Form>
	</ModalBody>
</Modal>

<Modal
	centered
	backdrop="static"
	header="Error: {repeatLocalModalText}"
	isOpen={repeatLocalModalOpen}
>
	<ModalBody>
		There was an error while executing the requested operation. You can repeat the action without
		notifying the other instance about it.
	</ModalBody>
	<ModalFooter>
		<Button
			color="secondary"
			onclick={() => {
				repeatLocalModalOpen = false;
				repeatLocalModalText = '';
				repeatLocalModalCallback = () => {};
			}}>Cancel</Button
		>
		<Button color="danger" onclick={repeatLocalModalCallback}>Repeat local only</Button>
	</ModalFooter>
</Modal>
