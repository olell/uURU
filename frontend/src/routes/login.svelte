<script lang="ts">
	import { Button, Form, FormGroup, Input, Modal, ModalBody } from '@sveltestrap/sveltestrap';
	import Register from './register.svelte';
	import { infoApiV1UserGet, loginApiV1UserLoginPost } from '../client';
	import { push_api_error, push_message } from '../messageService.svelte';
	import { user_info } from '../sharedState.svelte';

	let { isOpen = $bindable() } = $props();

	let showRegister = $state(window.location.hash.includes('register'));

	const toggle = () => (isOpen = !isOpen);
	let username = $state('');
	let password = $state('');

	async function handleLogin(event: Event) {
		event.preventDefault();

		const { data, error } = await loginApiV1UserLoginPost({
			body: { username, password },
			credentials: 'include'
		});

		if (error) {
			push_api_error(error, 'Failed to login!');
			return;
		}

		username = '';
		password = '';

		await retreiveUserData();
	}

	async function retreiveUserData() {
		const { data, error } = await infoApiV1UserGet({ credentials: 'include' });

		if (error) {
			push_api_error(error, 'Failed to retreive user information');
			return;
		}

		user_info.val = data;
		push_message({ color: 'success', title: 'Welcome!', message: `Hello ${data?.username} 👋` });
		isOpen = false;
	}
</script>

<Modal centered backdrop="static" header="Login" {isOpen} {toggle}>
	<ModalBody>
		<Form onsubmit={handleLogin}>
			<FormGroup floating label="Username">
				<Input bind:value={username} required />
			</FormGroup>
			<FormGroup floating label="Password">
				<Input bind:value={password} type="password" required minlength={10} />
			</FormGroup>
			<Button class="float-end" color="primary" type="submit">Login</Button>
		</Form>
		<Button
			color="link"
			onclick={(e) => {
				e.preventDefault();
				showRegister = true;
			}}>Or create a new account!</Button
		>
	</ModalBody>
</Modal>

<Register bind:isOpen={showRegister} />
