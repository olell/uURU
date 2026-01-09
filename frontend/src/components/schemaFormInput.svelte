<script lang="ts">
	import { Input, InputGroup } from "@sveltestrap/sveltestrap";
	import SchemaFormInput from "./schemaFormInput.svelte";

    let { prop, value = $bindable(), required } = $props();


    let selectedType = $state<string>("");

    
    $inspect(selectedType);
    //$inspect(value);

    $effect(() => {
        if (prop.anyOf) {
            let allowedTypes: string[] = prop.anyOf.map((x: {type: string}) => x.type)
            let t = typeof value;

            if (allowedTypes.includes(t)) selectedType = t;
            else if (value === null && allowedTypes.includes('null')) selectedType = 'null';
            else if (t == 'number' && allowedTypes.includes('integer')) selectedType = 'integer';
            console.log(t, allowedTypes);
            
        }
    })

    $effect(() => {
        if (selectedType === "null") {
            value = null;
        }
    })
</script>

{#if prop.enum}
    <select class="form-select" bind:value={value} required={required}>
        {#each prop.enum as opt}
            <option>{opt}</option>
        {/each}
    </select>
{:else if prop.anyOf}
    <InputGroup class="mb-1">
        <span class="input-group-text">Type</span>
        <select class="form-select" bind:value={selectedType} required={required}>
            {#each prop.anyOf as sub}
                <option>{sub.type}</option>
            {/each}
        </select>
    </InputGroup>
    <InputGroup>
        <span class="input-group-text">Value</span>
        <SchemaFormInput bind:value={value} prop={{type: selectedType}} required={required}></SchemaFormInput>
    </InputGroup>
{:else if prop.type == 'string'}
    <Input bind:value={value} pattern={prop.pattern} required={required} />
{:else if prop.type == 'integer'}
    <Input type="number" bind:value={value} required={required} />
{:else if prop.type == 'number'}
    <Input type="number" step="any" bind:value={value} required={required} />
{:else if prop.type == 'null'}
    <Input type="text" value="<null>" required readonly />
{/if}