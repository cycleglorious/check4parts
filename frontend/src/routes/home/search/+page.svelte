<script lang="ts">
	import SearchResultCard from '$lib/components/cards/search/SearchResultCard.svelte';
</script>

<SearchResultCard
	part={{
		name: 'Тормозний диск',
		description: 'Торомозний диск передній',
		brand: {
			id: '1',
			name: 'TRW'
		},
		details: [
			{ id: '1', value: '1234', title: 'Деталь 1', name: 'detail_1' },
			{ id: '2', value: '5678', title: 'Деталь 2', name: 'detail_2' }
		],
		id: '1',
		code: '1234567890',
		image: '/image 7.png'
	}}
	rests={[
		{
			id: '1',
			provider: {
				id: '1',
				name: 'Постачальник 1'
			},
			quantity: 10,
			delivery_time: '2 дні',
			price: 100
		},
		{
			id: '2',
			provider: {
				id: '2',
				name: 'Постачальник 2'
			},
			quantity: 5,
			delivery_time: '3 дні',
			price: 150
		}
	]}
/>
