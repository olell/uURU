<script lang="ts">
	import { Button, Form, FormGroup, Input, Label } from '@sveltestrap/sveltestrap';
	import { push_api_error, push_message } from '../../../messageService.svelte';
	import { changePasswordApiV1UserPasswordPatch } from '../../../client';

	let currentPassword = $state('');
	let newPassword = $state('');
	let repPassword = $state('');

	const handleSubmit = async (e: SubmitEvent) => {
		e.preventDefault();

		if (newPassword != repPassword) {
			push_message({ color: 'danger', title: 'Error!', message: 'Passwords do not match!' });
			return;
		}

		if (newPassword == currentPassword) {
			push_message({
				color: 'warning',
				title: 'Warning!',
				message: 'New password equals current password!'
			});
		}

		const { error } = await changePasswordApiV1UserPasswordPatch({
			credentials: 'include',
			body: {
				current_password: currentPassword,
				new_password: newPassword
			}
		});
		if (!!error) {
			push_api_error(error, 'Failed to change password!');
			return;
		}
		push_message({ color: 'success', title: 'Success!', message: 'Changed password' });
		currentPassword = '';
		newPassword = '';
		repPassword = '';
	};
</script>

<h1 class="fs-3">Account Settings</h1>
<hr />

<h1 class="fs-4">Change Password</h1>
<Form onsubmit={handleSubmit}>
	<FormGroup>
		<Label>Current Password</Label>
		<Input bind:value={currentPassword} type="password" minlength={10} required />
	</FormGroup>
	<FormGroup>
		<Label>New Password</Label>
		<Input bind:value={newPassword} type="password" minlength={10} required />
	</FormGroup>
	<FormGroup>
		<Label>Repeat Password</Label>
		<Input bind:value={repPassword} type="password" minlength={10} required />
	</FormGroup>
	<Button type="submit" color="primary" class="float-end">Save</Button>
</Form>
