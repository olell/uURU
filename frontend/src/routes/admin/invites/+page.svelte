<script lang="ts">
	import {
		Form,
		FormGroup,
		Icon,
		Input,
		InputGroup,
		InputGroupText,
		Label,
		Table
	} from '@sveltestrap/sveltestrap';
	import {
		createInviteApiV1UserInvitePost,
		deleteInviteApiV1UserInviteDelete,
		getInvitesApiV1UserInviteGet,
		type Invite,
		type InviteVariant
	} from '../../../client';
	import { push_api_error } from '../../../messageService.svelte';

	let invites = $state<Invite[]>([]);
	let selectedVariant = $state<InviteVariant>('time+count');
	let maxUses = $state(1);
	let validDays = $state(0);
	let validHours = $state(24);

	let created = $state<Invite | undefined>(undefined);

	const updateInvites = async () => {
		getInvitesApiV1UserInviteGet({ credentials: 'include' }).then(({ data, error }) => {
			if (error || data === undefined) {
				push_api_error(error, 'Failed to get invites!');
				return;
			}
			invites = data;
		});
	};

	$effect(() => {
		updateInvites();
	});

	const reprVariant = (variant: string) => {
		if (variant == 'time') return 'Time';
		if (variant == 'count') return 'Count';
		if (variant == 'time+count') return 'Time and count';
	};

	const reprValidity = (invite: Invite) => {
		let result = '';
		if (invite.variant?.includes('count')) {
			result += `Used ${invite.use_count}/${invite.max_uses}`;
		}
		if (invite.variant == 'time+count') {
			result += ' - ';
		}
		if (invite.variant?.includes('time')) {
			result += `Valid until ${invite.valid_until}`;
		}
		return result;
	};

	const handleSubmit = async (e: SubmitEvent) => {
		e.preventDefault();

		const body = {
			variant: selectedVariant,
			max_uses: selectedVariant.includes('count') ? maxUses : null,
			valid_days: selectedVariant.includes('time') ? validDays : null,
			valid_hours: selectedVariant.includes('time') ? validHours : null
		};

		const { data, error } = await createInviteApiV1UserInvitePost({
			credentials: 'include',
			body
		});

		if (error || data === undefined) {
			push_api_error(error, 'Failed to create invite');
			return;
		}
		created = data;
		await updateInvites();
	};

	const deleteInvite = async (invite: Invite) => {
		const { data, error } = await deleteInviteApiV1UserInviteDelete({
			credentials: 'include',
			query: {
				invite: invite.invite
			}
		});
		if (error) {
			push_api_error(error, 'Failed to delete invite');
			return;
		}
		await updateInvites();
	};
</script>

<h2>Invites</h2>
<hr />

<h3>Create a new Invite</h3>
<Form onsubmit={handleSubmit}>
	<FormGroup>
		<Label>Variant</Label>
		<select class="form-select" bind:value={selectedVariant}>
			<option value={'time'}>{reprVariant('time')}</option>
			<option value={'count'}>{reprVariant('count')}</option>
			<option value={'time+count'}>{reprVariant('time+count')}</option>
		</select>
	</FormGroup>
	{#if selectedVariant.includes('count')}
		<FormGroup>
			<Label>Max Uses:</Label>
			<Input type="number" bind:value={maxUses} required />
		</FormGroup>
	{/if}
	{#if selectedVariant.includes('time')}
		<FormGroup>
			<Label>Valid Days:Hours</Label>
			<InputGroup>
				<Input type="number" bind:value={validDays} required />
				<InputGroupText>:</InputGroupText>
				<Input type="number" bind:value={validHours} required />
			</InputGroup>
		</FormGroup>
	{/if}
	<FormGroup class="d-flex justify-content-end">
		<Input color="info" type="submit" value="Create Invite" />
	</FormGroup>
</Form>

{#if created}
	<hr />
	<h3>Created Invite</h3>
	<pre>Code: {created.invite}</pre>
{/if}
<hr />

<h3>All invites</h3>
<Table striped>
	<thead>
		<tr>
			<th scope="col">Code</th>
			<th scope="col">Variant</th>
			<th scope="col">Validity</th>
			<th scope="col">Delete</th>
		</tr>
	</thead>
	<tbody>
		{#each invites as invite (invite.id)}
			<tr>
				<td>{invite.invite}</td>
				<td>{reprVariant(invite.variant!)}</td>
				<td>{reprValidity(invite)}</td>
				<td
					><a href={'#'} onclick={deleteInvite(invite)} class="text-danger"
						><Icon name="trash3"></Icon></a
					></td
				>
			</tr>
		{/each}
	</tbody>
</Table>
