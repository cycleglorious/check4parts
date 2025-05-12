<script lang="ts">
	interface Props {
		part: Object;
	}
	let { part }: Props = $props();

	let numberInput = $state<HTMLInputElement>();
	let value = $state<number>(0);
	$inspect(value);
</script>

<div class="flex w-full items-center justify-between gap-2">
	<div
		class="number-input border-primary-950 flex h-8 flex-row items-center justify-center overflow-hidden rounded-lg border"
	>
		<button
			type="button"
			class="hover:bg-surface-100-900 p-2"
			onclick={() => {
				numberInput!.stepDown(1);
				value = numberInput!.valueAsNumber;
			}}
		>
			-
		</button>
		<input
			type="number"
			class="w-6 border-none bg-transparent p-0 text-center focus:outline-none"
			bind:value
			bind:this={numberInput}
			min="0"
		/>
		<button
			type="button"
			class="hover:bg-surface-100-900 p-2"
			onclick={() => {
				numberInput!.stepUp(1);
				value = numberInput!.valueAsNumber;
			}}
		>
			+
		</button>
	</div>
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

<style>
	input[type='number'] {
		-webkit-appearance: textfield;
		-moz-appearance: textfield;
		appearance: textfield;
	}

	input[type='number']::-webkit-inner-spin-button,
	input[type='number']::-webkit-outer-spin-button {
		-webkit-appearance: none;
	}
</style>
