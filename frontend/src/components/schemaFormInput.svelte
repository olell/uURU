<script lang="ts">
	import { Icon, Input, InputGroup } from "@sveltestrap/sveltestrap";
	import SchemaFormInput from "./schemaFormInput.svelte";

    let { prop, value = $bindable(), required, onEnter = () => {} } = $props();


    let selectedType = $state<string>("");
    let selectedSubProp = $state<any>(null);
    $inspect(selectedSubProp);


    $effect(() => {
        if (prop.anyOf) {
            let allowedTypes: string[] = prop.anyOf.map((x: {type: string}) => x.type)
            let t = typeof value;

            if (allowedTypes.includes(t)) selectedType = t;
            else if (value === null && allowedTypes.includes('null')) selectedType = 'null';
            else if (t == 'number' && allowedTypes.includes('integer')) selectedType = 'integer';
        }
    })

    $effect(() => {
        if (selectedType !== "" && prop.anyOf) {
            selectedSubProp = prop.anyOf.find((x:any) => x.type == selectedType);
        }
    })

    $effect(() => {
        if (selectedType === "null") {
            value = null;
        }
    })

    const keydown = (e: any) => {
        if (e.keyCode == 13) {
            onEnter()
        }
    }

    const addElement = () => {
        if (prop.type !== 'array') return;
        if (prop.items.type === 'string') value.push("");
        if (prop.items.type === 'integer' || prop.items.type === 'number') value.push(0);


    }

    const removeElement = (idx: number) => {
        if (prop.type !== 'array') return;
        if (idx < 0 || idx >= value.length) return;
        value.splice(idx, 1)
    }
</script>

{#if prop.enum}
    <select class="form-select" bind:value={value} required={required}>
        {#each prop.enum as opt}
            <option>{opt}</option>
        {/each}
    </select>
{:else if prop.anyOf}
    <InputGroup>
        <select class="form-select" style="max-width: 30%" bind:value={selectedType} required={required}>
            {#each prop.anyOf as sub}
                <option>{sub.type}</option>
            {/each}
        </select>
        <SchemaFormInput bind:value={value} prop={selectedSubProp || {type: selectedType}} required={required}></SchemaFormInput>
    </InputGroup>
{:else if prop.type == 'array'}
    <a href={'#'} class="text-success ms-2" onclick={addElement}><Icon name="plus-circle" /></a>
    {#if value.length > 0}
        {#each value as _, idx}
        <InputGroup class="mb-2">
            <span class="input-group-text" style="min-width: 2.5rem;">{idx+1}.</span>
            <SchemaFormInput bind:value={value[idx]} prop={prop.items} onEnter={addElement} required={required}></SchemaFormInput>
            <span class="input-group-text">
                <a href={'#'} class="text-danger" onclick={() => removeElement(idx)}><Icon name="trash3" /></a>
            </span>
        </InputGroup>
        {/each}
    {/if}
    
{:else if prop.type == 'string'}
    <Input bind:value={value} pattern={prop.pattern} onkeydown={keydown} required={required} />
{:else if prop.type == 'integer'}
    <Input type="number" bind:value={value} onkeydown={keydown} required={required} />
{:else if prop.type == 'number'}
    <Input type="number" step="any" bind:value={value} onkeydown={keydown} required={required} />
{:else if prop.type == 'null'}
    <Input type="text" value="<null>" required disabled readonly />
{/if}