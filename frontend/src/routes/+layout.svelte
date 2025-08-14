<script lang="ts">
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
		NavLink
	} from '@sveltestrap/sveltestrap';
	import { getSiteInfoApiV1SiteGet, infoApiV1UserGet } from '../client';
	import { site_info, user_info } from '../sharedState.svelte';

	let { children } = $props();
	let theme = $state<"dark" | "light">("dark");

	let navbarOpen = $state(true);

	function handleNavbarCollapse(event: any) {
		navbarOpen = event.detail.isOpen;
	}

	// load site info
	$effect(() => {
		getSiteInfoApiV1SiteGet()
			.then(({ data, error }) => {
				console.log(data, error);
				if (error === undefined && data !== undefined) {
					site_info.val = data;
				}
			})
			.catch((e) => {
				alert(e);
			});
	});

	// load user info
	$effect(() => {
		infoApiV1UserGet().then(({ data, error }) => {
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
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<Navbar color={theme} expand="md" container="md">
	<NavbarBrand href="/">
		<img src={favicon} alt="" width="30" height="24" class="d-inline-block align-text-top" />
		{site_info.val?.site_name} — µURU
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
				<NavItem>
					<NavLink href="/extension/own">Your Extensions</NavLink>
				</NavItem>
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
				<NavLink href="/user/login">Login</NavLink>
			</NavItem>
			{:else}
			<Dropdown>
				<DropdownToggle nav caret>{user_info.val?.username}</DropdownToggle>
				<DropdownMenu>
					<DropdownItem href="/user/settings">Settings</DropdownItem>
					<DropdownItem href="/user/logout">Logout</DropdownItem>
				</DropdownMenu>
			</Dropdown>
			{/if}
		</Nav>
	</Collapse>
</Navbar>

<div class="container mt-3">
	{@render children?.()}
</div>
