import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase }, params }) => {
	depends('supabase:db:company_provider');
	const { data, error } = await supabase
		.from('company_provider')
		.select('*,providers(*)')
		.eq('id', params.id)
		.single();
	if (error) {
		return { supplier: {} };
	}
	return {
		supplier: data ?? {}
	};
};

export const actions = {
	delete: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();
		const id = formData.get('id');

		const { error } = await supabase.from('company_provider').delete().eq('id', id);

		if (error) {
			return { success: false, message: error.message };
		} else {
			return redirect(303, '/home/settings/suppliers');
		}
	},
	editState: async ({ request, locals: { supabase } }) => {
		const form_data = await request.formData();

		const id = form_data.get('id')?.toString();
		const state = form_data.get('state')?.toString();

		const { error } = await supabase.from('company_provider').update({ state }).eq('id', id);
		if (error) {
			return { success: false, message: error.message };
		} else {
			return { success: true, message: 'updated' };
		}
	},
	edit: async ({ request, locals: { supabase } }) => {
		const formData = await request.formData();
		const id = formData.get('id')?.toString();
		const data_props = JSON.parse(formData.get('data_props')?.toString() || '{}') as DataProps[];
		const new_data = Object.fromEntries(
			Array.from(formData.entries().filter(([key]) => key !== 'id' && key !== 'data_props'))
		);

		const new_data_props = data_props.map((item) => {
			item.value = new_data[item.name] as string;
			return item;
		});

		const { data, error } = await supabase
			.from('company_provider')
			.update({ data: new_data_props })
			.eq('id', id)
			.select();
		``;

		if (error) {
			return { success: false, message: error.message };
		} else {
			return { success: true, message: 'updated' };
		}
	}
};
