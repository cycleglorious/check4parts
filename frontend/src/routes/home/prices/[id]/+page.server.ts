import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabasePrices }, request, params }) => {
	const history_id = params.id;
	const { data: price_history, error: historyError } = await supabasePrices
		.from('price_history')
		.select('*, providers(*)')
		.eq('id', history_id)
		.single();

	if (price_history.status === 'actual') {
		const {
			data: price,
			error,
			count
		} = await supabasePrices
			.from('prices')
			.select('*', { count: 'exact' })
			.eq('history_id', history_id)
			.limit(100);

		const { data: warehouses, error: warehousesError } = await supabasePrices
			.from('warehouses')
			.select('*')
			.order('name')
			.eq('provider_id', price?.[0]?.provider_id || 0);

		return {
			price: price || [],
			price_history: price_history || [],
			warehouses: warehouses || [],
			count: count || 0
		};
	}
	return {
		price: [],
		price_history: price_history || [],
		warehouses: [],
		count: 0
	};
};
