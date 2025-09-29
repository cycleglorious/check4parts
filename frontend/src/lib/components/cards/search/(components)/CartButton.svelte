<script lang="ts">
	import NumberInput from '$lib/components/inputs/table/NumberInput.svelte';

	interface Props {
		part: Object;
	}
	let { part }: Props = $props();

	let value = $state<number>(0);
	$inspect(value);
</script>

<div class="flex w-full items-center justify-between gap-2">
	<NumberInput bind:value />
	<div class="flex flex-col gap-2">
		<button
			type="button"
			class="btn-icon preset-filled-primary-50-950"
			disabled={value === 0}
			onclick={() => {
				console.log('Add to cart:', value, part);
			}}
		>
			<img src="/cart.svg" alt="Add to cart" class="size-6" />
		</button>
	</div>
</div>
