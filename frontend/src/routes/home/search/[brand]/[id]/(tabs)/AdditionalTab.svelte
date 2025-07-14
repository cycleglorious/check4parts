<script lang="ts">
	interface Props {
		additional: {
			id: string;
			min_quantity: number;
			name: string;
			code: string;
		}[];
	}

	let { additional }: Props = $props();
</script>

<div class="border-primary-950 overflow-hidden rounded-xl border-2">
	<div class="max-h-[53vh] overflow-y-auto">
		<table class="table border-collapse">
			<thead class="bg-primary-950 sticky top-0 z-10">
				<tr class="text-primary-50">
					<th>Код частини</th>
					<th>Необхідна кількість</th>
					<th>Назва</th>
				</tr>
			</thead>
			<tbody class="!divide-primary-950 !divide-y-2">
				{#each additional as addon}
					<tr class="divide-primary-950 group hover:bg-primary-50 w-full divide-x-2">
						<td  >{addon.code}</td>
						<td  >{addon.min_quantity}</td>
						<td  >{addon.name}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
