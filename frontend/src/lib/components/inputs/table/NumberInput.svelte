<script lang="ts">
	interface Props {
		value: number;
	}

	let { value = $bindable(0) }: Props = $props();

	let numberInput = $state<HTMLInputElement>();
</script>

<div
	class="number-input border-primary-950 flex h-8 w-fit flex-row items-center justify-center overflow-hidden rounded-lg border"
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
