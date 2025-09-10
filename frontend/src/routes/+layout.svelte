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
		Icon,
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
		logoutApiV1UserLogoutGet,
		getPagesApiV1PagesGet
	} from '../client';
	import { isMobile, pages, settings, user_info } from '../sharedState.svelte';
	import Login from './login.svelte';
	import { messages, push_message } from '../messageService.svelte';
	import { fade } from 'svelte/transition';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { navigating } from '$app/stores';
	import { resolve } from '$app/paths';
	import { client } from '../client/client.gen';
	import { dev } from '$app/environment';

	if (!dev) client.setConfig({ ...client.getConfig(), baseUrl: '/' });

	let { children } = $props();
	let theme = $state<'dark' | 'light'>('dark');

	let showLogin = $state(false);

	let navbarOpen = $state(false);

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
		getPagesApiV1PagesGet().then(({ data, error }) => {
			if (error === undefined && data !== undefined) {
				pages.val = data;
				console.log(pages);
			}
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
				goto(resolve('/'));
			})
			.catch((e) => {
				push_message({ color: 'danger', message: 'Failed to logout!', title: 'Error!' });
			});
	}

	function checkViewport() {
		isMobile.val = window.innerWidth < 768; // Bootstrap md breakpoint
	}

	onMount(() => {
		checkViewport();
		window.addEventListener('resize', checkViewport);

		return () => {
			window.removeEventListener('resize', checkViewport);
		};
	});

	$effect(() => {
		if ($navigating) navbarOpen = false;
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>{settings.val?.SITE_NAME} - uURU</title>
</svelte:head>

{#if settings.val}
	<Navbar color={theme} expand="md" container="md">
		<NavbarBrand href={resolve('/')}>
			<img src={favicon} alt="" width="30" height="24" class="d-inline-block align-text-top" />
			{settings.val?.SITE_NAME} — µURU
		</NavbarBrand>
		<NavbarToggler onclick={() => (navbarOpen = !navbarOpen)} />
		<Collapse
			isOpen={navbarOpen || !isMobile.val}
			expand="md"
			navbar
			on:update={handleNavbarCollapse}
		>
			<Nav navbar>
				<NavItem>
					<NavLink href={resolve('/')}>Phonebook</NavLink>
				</NavItem>
				<NavItem>
					<NavLink href={resolve('/map')}>Map</NavLink>
				</NavItem>
				{#if user_info.val}
					<Dropdown>
						<DropdownToggle nav caret>Extensions</DropdownToggle>
						<DropdownMenu>
							<DropdownItem href={resolve('/extensions')}>Your Extensions</DropdownItem>
							<DropdownItem href={resolve('/extensions/new')}>Create a new Extension</DropdownItem>
						</DropdownMenu>
					</Dropdown>
				{/if}
				{#if Object.keys(pages.val).length !== 0}
					<Dropdown>
						<DropdownToggle nav caret>{settings.val.PAGES_TITLE}</DropdownToggle>
						<DropdownMenu>
							{#each Object.keys(pages.val) as title}
								<DropdownItem href={resolve(`/pages?page=${title}`)}>{title}</DropdownItem>
							{/each}
						</DropdownMenu>
					</Dropdown>
				{/if}
				{#if user_info.val && user_info.val.role == 'admin'}
					<Dropdown>
						<DropdownToggle nav caret>Admin</DropdownToggle>
						<DropdownMenu>
							<DropdownItem href={resolve('/admin/user')}>Users</DropdownItem>
							<DropdownItem href={resolve('/admin/extensions')}>Extensions</DropdownItem>
							{#if settings.val.LIMIT_REGISTRATION}
								<DropdownItem href={resolve('/admin/invites')}>Invites</DropdownItem>
							{/if}
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
						<DropdownToggle nav caret>
							<Icon name="person-circle" class="me-1"></Icon>
							{user_info.val?.username}
						</DropdownToggle>
						<DropdownMenu>
							<DropdownItem href={resolve('/user/settings')}>Settings</DropdownItem>
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
