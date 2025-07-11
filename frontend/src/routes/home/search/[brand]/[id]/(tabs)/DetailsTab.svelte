<!-- details: [
				{ id: '1', value: '1234', title: 'Деталь 1', name: 'detail_1' },
				{ id: '2', value: '5678', title: 'Деталь 2', name: 'detail_2' }
			], -->

<script lang="ts">
	interface Props {
		details: {
			id?: string;
			value: string;
			title: string;
			name: string;
		}[];
	}

	let { details }: Props = $props();
</script>

{#snippet tableRow(name: string, value: string)}
	<tr class="odd:bg-gray-50 even:bg-white">
		<td class="text-primary-950-50 p-4 font-bold">{name}</td>
		<td class="p-4 pl-10 font-light">{value}</td>
	</tr>
{/snippet}

<table class="text-left text-sm text-gray-500 rtl:text-right">
	<tbody class="">
		{#each details as detail}
			{@render tableRow(detail.title, detail.value)}
		{/each}
	</tbody>
</table>
