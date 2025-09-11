<script lang="ts">
	import {
		Button,
		Form,
		FormGroup,
		FormText,
		Input,
		Modal,
		ModalBody,
		ModalFooter
	} from '@sveltestrap/sveltestrap';
	import { tick } from 'svelte';
	import { push_api_error, push_message } from '../messageService.svelte';
	import { registerApiV1UserRegisterPost } from '../client';
	import { settings } from '../sharedState.svelte';

	let { isOpen = $bindable() } = $props();

	const toggle = () => (isOpen = !isOpen);

	let username = $state('');
	let password = $state('');
	let password_rep = $state('');

	let invite = $state('');

	let passwords_match = $derived<boolean | undefined>(
		password ? password == password_rep : undefined
	);

	async function handleRegister(event: Event) {
		event.preventDefault();

		if (!passwords_match) {
			push_message({ color: 'danger', title: 'Hint!', message: "Passwords don't match!" });
			return;
		}

		const { data, error } = await registerApiV1UserRegisterPost({
			body: {
				username,
				password,
				role: 'user',
				invite: settings.val?.LIMIT_REGISTRATION ? invite : null
			},
			credentials: 'include'
		});

		if (error) {
			push_api_error(error, 'Failed to register account!');
			return;
		}

		push_message({
			color: 'success',
			title: 'Registered!',
			message: `Welcome ${data.username}! Your account was created 🎉`
		});

		username = '';
		password = '';
		password_rep = '';

		isOpen = false;
	}
</script>

<Modal centered backdrop="static" header="Register" {isOpen} {toggle}>
	<Form validated={passwords_match} onsubmit={handleRegister}>
		<ModalBody>
			<FormGroup floating label="Username">
				<Input bind:value={username} required />
			</FormGroup>
			<FormGroup floating label="Password">
				<Input bind:value={password} type="password" required minlength={10} />
			</FormGroup>
			<FormGroup floating label="Repeat Password">
				<Input bind:value={password_rep} type="password" required minlength={10} />
			</FormGroup>
			{#if settings.val?.LIMIT_REGISTRATION}
				<hr />
				<FormGroup floating label="Invite Code">
					<Input bind:value={invite} type="text" required minlength={10} />
					<FormText>
						This instance requires an invite code to create a new account, please ask an
						administrator to obtain such a code!
					</FormText>
				</FormGroup>
			{/if}
		</ModalBody>
		<ModalFooter>
			<Button color="primary" type="submit">Create Account</Button>
		</ModalFooter>
	</Form>
</Modal>
