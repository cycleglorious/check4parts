<script lang="ts">
	import NumberInput from '$lib/components/inputs/table/NumberInput.svelte';
	import RestsRow from './RestsRow.svelte';

	interface Props {
		rests: {
			id: string;
			provider: {
				id: string;
				name: string;
			};
			quantity: number;
			delivery_time: string;
			price: number;
		}[];
	}

	let { rests }: Props = $props();
</script>

<div class="border-primary-950 overflow-hidden rounded-xl border-2">
	<div class="max-h-[53vh] overflow-y-auto">
		<table class="table border-collapse">
			<thead class="bg-primary-950 sticky top-0 z-10">
				<tr class="text-primary-50">
					<th>Постачальник</th>
					<th>Наявність</th>
					<th>Термін доставики</th>
					<th>Ціна (грн)</th>
					<th class="w-16">Кількість</th>
					<th class="w-14"></th>
				</tr>
			</thead>
			<tbody class="!divide-primary-950 !divide-y-2">
				{#each rests as rest}
					<RestsRow {rest} />
				{/each}
			</tbody>
		</table>
	</div>
</div>
