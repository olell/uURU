<script lang="ts">
	import { dev } from '$app/environment';
	import { FormGroup, Label } from '@sveltestrap/sveltestrap';
	import SchemaFormInput from './schemaFormInput.svelte';

	const { schema, value = $bindable() } = $props();

	const isRequired = (property: string) => schema?.required?.includes(property);
</script>

{#if schema.description}
<span style="white-space: pre-line">{schema.description}</span>
<hr/>
{/if}
{#each Object.keys(schema.properties as object) as property}
	{@const prop = schema.properties[property]}
	<FormGroup>
		<Label>{prop.title} {isRequired(property) ? ' *' : ''}</Label>
		<SchemaFormInput required={isRequired(property)} prop={prop} bind:value={value[property]}></SchemaFormInput>
	</FormGroup>
{/each}

{#if dev}
<pre>
{JSON.stringify(schema, null, 2)}
</pre>
{/if}