<script lang="ts">
	import { page, updated } from '$app/state';
	import { Button, Form, FormGroup, Input, Label } from '@sveltestrap/sveltestrap';
	import {
		infoApiV1UserGet,
		type UserUpdate,
		type UserPublic,
		updateApiV1UserPatch,
		deleteApiV1UserDelete
	} from '../../../../client';
	import { push_api_error, push_message } from '../../../../messageService.svelte';
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';

	const { id } = page.params;
	let user = $state<UserPublic>();

	let updateData = $state<UserUpdate>({});

	$effect(() => {
		infoApiV1UserGet({
			credentials: 'include',
			query: { user_id: id }
		}).then(({ data, error }) => {
			if (!!error) {
				push_api_error(error, 'Failed to get user data');
			}
			user = data!;
			updateData.username = data!.username;
			updateData.role = data!.role;
		});
	});

	const handleSave = async (e: SubmitEvent) => {
		e.preventDefault();
		if (!user) return;
		// remove empty attrs
		let data = Object.fromEntries(Object.entries(updateData).filter(([_, v]) => !!v));

		const { error } = await updateApiV1UserPatch({
			credentials: 'include',
			query: { user_id: user.id },
			body: data
		});

		if (!!error) {
			push_api_error(error, 'Failed to update user!');
		}

		push_message({
			color: 'success',
			title: 'Success!',
			message: `Updated user ${user?.username} successfully!`
		});
		goto(resolve('/admin/user'));
	};

	const handleDelete = async () => {
		if (!user) return;
		const { error } = await deleteApiV1UserDelete({
			credentials: 'include',
			query: { user_id: user!.id }
		});
		if (!!error) {
			push_api_error(error, 'Failed to delete user!');
			return;
		}
		push_message({
			color: 'success',
			title: 'Success!',
			message: `Deleted user ${user.username}!`
		});
		goto(resolve('/admin/user'));
	};
</script>

<Form onsubmit={handleSave}>
	<FormGroup>
		<Label>Username</Label>
		<Input bind:value={updateData.username} />
	</FormGroup>
	<FormGroup>
		<Label>Role</Label>
		<select class="form-select" bind:value={updateData.role}>
			<option value="admin">Admin</option>
			<option value="user">User</option>
		</select>
	</FormGroup>
	<FormGroup>
		<Label>Password</Label>
		<Input type="password" bind:value={updateData.password} />
	</FormGroup>
	<Button type="submit" color="primary" class="float-end">Save</Button>
</Form>

<Button color="danger" class="float-end me-2" onclick={handleDelete}>Delete User</Button>
