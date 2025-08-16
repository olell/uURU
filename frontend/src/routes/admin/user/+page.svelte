<script lang="ts">
	import { Input, Table } from '@sveltestrap/sveltestrap';
	import { allUsersApiV1UserAllGet, type UserPublic } from '../../../client';
	import { push_api_error, push_message } from '../../../messageService.svelte';
	import { goto } from '$app/navigation';

	let query = $state('');
	let users = $state<UserPublic[]>([]);

	let filteredUser = $derived(users.filter((u) => u.username.toLowerCase().includes(query)));

	$effect(() => {
		allUsersApiV1UserAllGet({ credentials: 'include' })
			.then(({ data, error }) => {
				if (!!error) {
					push_api_error(error, 'Failed to get user data!');
					return;
				}
				users = data!;
			})
			.catch(() => {
				push_message({ color: 'danger', title: 'Error!', message: 'Failed to get user data!' });
			});
	});
</script>

<h1 class="fs-3">All Users</h1>
<hr />

<Input type="text" bind:value={query} placeholder="Search users" />

<Table striped hover>
	<thead>
		<tr>
			<th scope="col">Username</th>
			<th scope="col">Role</th>
		</tr>
	</thead>
	<tbody>
		{#each filteredUser as user (user.id)}
			<tr onclick={() => goto(`/admin/user/${user.id}`)}>
				<td>{user.username}</td>
				<td>{user.role}</td>
			</tr>
		{/each}
	</tbody>
</Table>
