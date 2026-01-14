<script>
    import { InputGroup } from "@sveltestrap/sveltestrap";

    export let nested = false;
</script>

{#if !nested}
    <InputGroup>
        <slot />
    </InputGroup>
{:else}
    <slot />
{/if}