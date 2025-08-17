<script lang="ts">
	import { FormGroup, Input, Label } from '@sveltestrap/sveltestrap';

	const { schema, value = $bindable() } = $props();
</script>

{#each Object.keys(schema.properties as object) as property}
	{@const prop = schema.properties[property]}
	<FormGroup>
		<Label>{prop.title}</Label>
		{#if prop.enum}
			<select class="form-select" bind:value={value[property]} required>
				{#each prop.enum as opt}
					<option>{opt}</option>
				{/each}
			</select>
		{:else if prop.type == 'string'}
			<Input bind:value={value[property]} pattern={prop.pattern} required />
		{:else if prop.type == 'integer'}
			<Input type="number" bind:value={value[property]} required />
		{:else if prop.type == 'number'}
			<Input type="number" step="any" bind:value={value[property]} required />
		{/if}
	</FormGroup>
{/each}
