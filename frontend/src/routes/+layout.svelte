<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { getSiteInfoApiV1SiteGet } from '../client';
	import { site_info } from '../sharedState.svelte';

	let { children } = $props();

	$effect(() => {
		getSiteInfoApiV1SiteGet().then(({data, error}) => {
			console.log(data, error)
			if (error === undefined && data !== undefined) {
				site_info.val = data;
			}
		}).catch((e) => {
			alert(e);
		})
	})
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
	<div class="container">
		<a class="navbar-brand" href="/">
			<img src={favicon} alt="" width="30" height="24" class="d-inline-block align-text-top" />
			{site_info.val?.site_name} — µURU</a
		>
		<button
			class="navbar-toggler"
			type="button"
			data-bs-toggle="collapse"
			data-bs-target="#navbarSupportedContent"
			aria-controls="navbarSupportedContent"
			aria-expanded="false"
			aria-label="Toggle navigation"
		>
			<span class="navbar-toggler-icon"></span>
		</button>
		<div class="collapse navbar-collapse" id="navbarSupportedContent">
			<ul class="navbar-nav me-auto mb-2 mb-lg-0">
				<li class="nav-item">
					<a class="nav-link active" aria-current="page" href="/">Phonebook</a>
				</li>
				<li class="nav-item">
					<a class="nav-link" aria-current="page" href="/map">Map</a>
				</li>
				<!-- {% if user is defined and user is not none %} -->
				<li class="nav-item">
					<a class="nav-link" href="/extension/own">Your Extensions</a>
				</li>
				<!-- {% endif %} -->
				<!-- {% if pages.available() %} -->
				<li class="nav-item dropdown">
					<a
						class="nav-link dropdown-toggle"
						href="#"
						role="button"
						data-bs-toggle="dropdown"
						aria-expanded="false"
					>
						PAGES
					</a>
					<ul class="dropdown-menu">
						<!-- {% for page in pages.get_all() %} -->
						<li><a class="dropdown-item" href="/pages/page">page</a></li>
						<!-- {% endfor %} -->
					</ul>
				</li>
				<!-- {% endif %} -->
				<!-- {% if user is defined and user.role == "admin" %} -->
				<li class="nav-item dropdown">
					<a
						class="nav-link dropdown-toggle"
						href="#"
						role="button"
						data-bs-toggle="dropdown"
						aria-expanded="false"
					>
						Admin
					</a>
					<ul class="dropdown-menu">
						<li><a class="dropdown-item" href="/admin/users">Users</a></li>
						<li><a class="dropdown-item" href="/admin/extensions">Extensions</a></li>
					</ul>
				</li>
				<!-- {% endif %} -->
			</ul>
			<ul class="navbar-nav navbar-end">
				<!-- {% if user is not defined or user is none %} -->
				<li class="nav-item float-end">
					<a class="nav-link" href="/user/login">Login</a>
				</li>
				<!-- {% else %}
        <li class="nav-item dropdown">
          <a
            class="nav-link dropdown-toggle"
            href="#"
            role="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            {{ user.username }}
          </a>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="/user/settings">Settings</a></li>
            <li><a class="dropdown-item" href="/user/logout">Logout</a></li>
          </ul>
        </li>
        {% endif %} -->
			</ul>
		</div>
	</div>
</nav>

<div class="container">
	{@render children?.()}
</div>
