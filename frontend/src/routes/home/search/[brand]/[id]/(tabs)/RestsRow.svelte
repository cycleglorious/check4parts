<script lang="ts">
	import NumberInput from '$lib/components/inputs/table/NumberInput.svelte';

	interface Props {
		rest: {
			id: string;
			provider: {
				id: string;
				name: string;
			};
			delivery_time: string;
			price: number;
			quantity: number;
		};
	}

	let { rest }: Props = $props();
	let value: number = $state(0);
</script>

<tr class="divide-primary-950 group hover:bg-primary-50 w-full divide-x-2">
	<td>{rest.provider.name}</td>
	<td>{rest.quantity}</td>
	<td>{rest.delivery_time}</td>
	<td>{rest.price}</td>
	<td><NumberInput bind:value /></td>
	<td>
		<button
			type="button"
			class="btn-icon preset-filled-primary-50-950"
			disabled={value === 0}
			onclick={() => {
				console.log('Add to cart:', value, rest.id);
			}}
		>
			<img src="/cart.svg" alt="Add to cart" class="size-6" />
		</button>
	</td>
</tr>
