<script lang="ts">
	import { goto } from '$app/navigation';

	interface Props {
		crosses: {
			name: string;
			image?: string;
			id: string;
			code: string;
			quantity_in_pack: number;
			group: string;
			brand: string;
		}[];
	}

	let { crosses }: Props = $props();
</script>

<div class="overflow-auto">
	<table class="w-full table-auto border-collapse rtl:text-right">
		<thead>
			<tr>
				<th class="px-5 text-center font-normal tracking-wider text-gray-500">
					Назва | код товару
				</th>
				<th class="px-5 text-center font-normal tracking-wider text-gray-500">
					Кількість в упаковці
				</th>
				<th class="px-5 text-center font-normal tracking-wider text-gray-500"> Група товарів </th>
				<th class="px-5 text-center font-normal tracking-wider text-gray-500"> Виробник </th>
			</tr>
		</thead>
		<tbody class="bg-white">
			{#each crosses as cross}
				<tr
					class="bg-primary-50 hover:bg-primary-100 border-5 border-white"
					onclick={() => {
						goto(`/home/search/${cross.brand}/${cross.id}`);
					}}
				>
					<td class="rounded-l-2xl p-2 text-center">
						<div class="grid grid-cols-[auto_1fr] gap-2">
              {#if cross.image}
							<img src={cross.image} alt={cross.name} class="size-12 rounded-md object-cover object-center" />
              {/if}
							<div>
								<p class="text-left font-bold">{cross.name}</p>
								<p class="text-left font-light">
									Код: {cross.code}
								</p>
							</div>
						</div></td
					>
					<td class="p-2 text-center">{cross.quantity_in_pack} шт</td>
					<td class="p-2 text-center">{cross.group}</td>
					<td class="rounded-r-2xl p-2 text-center">{cross.brand}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
