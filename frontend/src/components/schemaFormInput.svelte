<script lang="ts">
	import { Icon, Input, InputGroup } from "@sveltestrap/sveltestrap";
	import NestedInputGroup from "./nestedInputGroup.svelte";
	import SchemaFormInput from "./schemaFormInput.svelte";

    let { prop, value = $bindable(), required, onEnter = () => {}, nested=false } = $props();


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

    let objectEntries = $state<[string, any][]>([]);
    
    $effect(() => {
        if (prop.type === 'object' && !!value) {
            objectEntries = Object.entries(value);
        }
    })

    $effect(() => {
        if (prop.type === 'object') {
            const obj = Object.fromEntries(objectEntries);
            if (JSON.stringify(obj) !== JSON.stringify(value)) {
                value = obj;
            }
        }
    })

    const addKey = () => {
        if (prop.type !== 'object') return;
        if (objectEntries.some(x => x[0] === '')) return;
        if (prop.additionalProperties.type === 'string') objectEntries.push(["", ""]);
        else if (prop.additionalProperties.type === 'integer' || prop.additionalProperties.type === 'number') objectEntries.push(["", 0]);
        else objectEntries.push(["", null])
    }

    const removeKey = (idx: number) => {
        if (prop.type !== 'object') return;
        if (idx < 0 || idx >= objectEntries.length) return;
        objectEntries.splice(idx, 1);
    }
</script>

{#if prop.enum}
    <select class="form-select" bind:value={value} required={required}>
        {#each prop.enum as opt}
            <option>{opt}</option>
        {/each}
    </select>
{:else if prop.anyOf}
    <NestedInputGroup nested={nested}>
        <select class="form-select" style="max-width: 30%" bind:value={selectedType} required={required}>
            {#each prop.anyOf as sub}
                <option>{sub.type}</option>
            {/each}
        </select>
        <SchemaFormInput bind:value={value} prop={selectedSubProp || {type: selectedType}} required={required}></SchemaFormInput>
    </NestedInputGroup>
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
{:else if prop.type == 'object'}
    <a href={'#'} class="text-success ms-2" onclick={addKey}><Icon name="plus-circle" /></a>
    {#if objectEntries.length > 0}
        {#each objectEntries as _, idx}
        <InputGroup class="mb-2">
            <span class="input-group-text">Key:</span>
            {#if !!prop.propertyNames?.enum}
                <select class="form-select" bind:value={objectEntries[idx][0]} required={required}>
                    {#each prop.propertyNames.enum as key}
                        <option>{key}</option>
                    {/each}
                </select>
            {:else}
            <Input bind:value={objectEntries[idx][0]} required={required} />
            {/if}
            <span class="input-group-text">Value:</span>
            <SchemaFormInput bind:value={objectEntries[idx][1]} prop={prop.additionalProperties} onEnter={addKey} required={required} nested={true}></SchemaFormInput>
            <span class="input-group-text">
                <a href={'#'} class="text-danger" onclick={() => removeKey(idx)}><Icon name="trash3" /></a>
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