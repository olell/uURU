<script lang="ts">
	import 'halfmoon/css/halfmoon.min.css';
	import 'halfmoon/css/cores/halfmoon.modern.css';

	import favicon from '$lib/assets/favicon.svg';
	import {
		Button,
		Collapse,
		colorMode,
		Container,
		Dropdown,
		DropdownItem,
		DropdownMenu,
		DropdownToggle,
		Nav,
		Navbar,
		NavbarBrand,
		NavbarToggler,
		NavItem,
		NavLink,
		Toast,
		ToastBody,
		ToastHeader
	} from '@sveltestrap/sveltestrap';
	import {
		getSettingsApiV1SettingsGet,
		infoApiV1UserGet,
		logoutApiV1UserLogoutGet
	} from '../client';
	import { settings, user_info } from '../sharedState.svelte';
	import Login from './login.svelte';
	import { messages, push_message } from '../messageService.svelte';
	import { fade } from 'svelte/transition';
	import { goto } from '$app/navigation';

	let { children } = $props();
	let theme = $state<'dark' | 'light'>('dark');

	let showLogin = $state(false);

	let navbarOpen = $state(true);

	function handleNavbarCollapse(event: any) {
		navbarOpen = event.detail.isOpen;
	}

	// load site info
	$effect(() => {
		getSettingsApiV1SettingsGet()
			.then(({ data, error }) => {
				if (error === undefined && data !== undefined) {
					settings.val = data;
				}
			})
			.catch((e) => {
				push_message({
					color: 'danger',
					title: 'Error!',
					message: 'Failed to read settings data!'
				});
			});
	});

	// load user info
	$effect(() => {
		infoApiV1UserGet({ credentials: 'include' }).then(({ data, error }) => {
			if (error === undefined && data !== undefined) {
				user_info.val = data;
			}
		});
	});

	// set theme based on system preference
	$effect(() => {
		const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)');
		theme = prefersDarkMode.matches ? 'dark' : 'light';

		prefersDarkMode.addEventListener('change', (event) => {
			theme = event.matches ? 'dark' : 'light';
		});
	});
	$effect(() => {
		$colorMode = theme;
	});

	function logout() {
		logoutApiV1UserLogoutGet({ credentials: 'include' })
			.then(() => {
				user_info.val = undefined;
				goto('/');
			})
			.catch((e) => {
				push_message({ color: 'danger', message: 'Failed to logout!', title: 'Error!' });
			});
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if settings.val}
	<Navbar color={theme} expand="md" container="md">
		<NavbarBrand href="/">
			<img src={favicon} alt="" width="30" height="24" class="d-inline-block align-text-top" />
			{settings.val?.SITE_NAME} — µURU
		</NavbarBrand>
		<NavbarToggler on:click={() => (navbarOpen = !navbarOpen)} />
		<Collapse isOpen={navbarOpen} expand="md" navbar on:update={handleNavbarCollapse}>
			<Nav navbar>
				<NavItem>
					<NavLink href="/">Phonebook</NavLink>
				</NavItem>
				<NavItem>
					<NavLink href="/map">Map</NavLink>
				</NavItem>
				{#if user_info.val}
					<Dropdown>
						<DropdownToggle nav caret>Extensions</DropdownToggle>
						<DropdownMenu>
							<DropdownItem href="/extensions">Your Extensions</DropdownItem>
							<DropdownItem>Create a new Extension</DropdownItem>
						</DropdownMenu>
					</Dropdown>
				{/if}
				<!-- {% if pages.available() %}
			<Dropdown>
				<DropdownToggle nav caret>Pages TODO: Title</DropdownToggle>
				<DropdownMenu>
					{#each ...}
					<DropdownItem href="/pages?page=foo">page title</DropdownItem>
					{/each}
				</DropdownMenu>
			</Dropdown>
			{% endif %} -->
				{#if user_info.val && user_info.val.role == 'admin'}
					<Dropdown>
						<DropdownToggle nav caret>Admin</DropdownToggle>
						<DropdownMenu>
							<DropdownItem href="/admin/user">Users</DropdownItem>
							<DropdownItem href="/admin/extensions">Extensions</DropdownItem>
						</DropdownMenu>
					</Dropdown>
				{/if}
			</Nav>
			<Nav class="ms-auto" navbar>
				{#if !user_info.val}
					<NavItem>
						<NavLink
							onclick={() => {
								showLogin = true;
							}}>Login</NavLink
						>
					</NavItem>
				{:else}
					<Dropdown>
						<DropdownToggle nav caret>{user_info.val?.username}</DropdownToggle>
						<DropdownMenu>
							<DropdownItem href="/user/settings">Settings</DropdownItem>
							<DropdownItem onclick={logout}>Logout</DropdownItem>
						</DropdownMenu>
					</Dropdown>
				{/if}
			</Nav>
		</Collapse>
	</Navbar>

	<Login bind:isOpen={showLogin} />

	<div style="bottom: 0; right: 0; position: fixed; z-index: 9001;">
		{#each messages as message (message.key)}
			<div class="p-3 mb-1" transition:fade>
				<Toast class="me-1">
					<ToastHeader icon={message.color}>{message.title}</ToastHeader>
					<ToastBody>{message.message}</ToastBody>
				</Toast>
			</div>
		{/each}
	</div>

	<div class="container mt-3">
		{@render children?.()}
	</div>
{/if}
