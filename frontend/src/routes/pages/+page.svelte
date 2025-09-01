<script lang="ts">
	import { page } from '$app/stores';
	import { pages } from '../../sharedState.svelte';

	$: name = $page.url.searchParams.get('page');

	function addBootstrapClasses(html: string) {
		return html
			.replace(/<table>/g, '<table class="table table-bordered table-striped">')
			.replace(/<ul>/g, '<ul class="list-group list-group-flush">')
			.replace(/<ol>/g, '<ol class="list-group list-group-numbered">')
			.replace(/<li>/g, '<li class="list-group-item">');
	}
</script>

<div class="container mt-4">
	<div class="markdown-body">{@html addBootstrapClasses(pages.val[name] ?? '')}</div>
</div>

<style>
	.markdown-body h1,
	.markdown-body h2,
	.markdown-body h3 {
		margin-top: 1.5rem;
		margin-bottom: 1rem;
		font-weight: 500;
	}
	.markdown-body p {
		margin-bottom: 1rem;
	}
	.markdown-body pre {
		padding: 1rem;
		border-radius: 0.5rem;
	}
	.markdown-body code {
		padding: 0.2em 0.4em;
		border-radius: 0.3em;
	}
</style>
