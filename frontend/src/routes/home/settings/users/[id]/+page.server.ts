import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase }, params }) => {
	depends('supabase:db:staff');
	const user_id = params.id;
	const { data: user } = await supabase
		.from('staff')
		.select('*,roles(name),trading_points(*)')
		.eq('id', user_id)
		.single();

	depends('supabase:db:roles');
	const { data: roles } = await supabase.from('roles').select('*').order('name');

	depends('supabase:db:trading-points');
	const { data: points } = await supabase.from('trading_points').select('*').order('name');
	return { user: user ?? {}, roles: roles ?? [], points: points ?? [] };
};

export const actions = {
	edit: async ({ request, locals: { supabase } }) => {
		const form_data = await request.formData();

		const id = form_data.get('id')?.toString();
		const first_name = form_data.get('first_name')?.toString();
		const last_name = form_data.get('last_name')?.toString();
		const middle_name = form_data.get('middle_name')?.toString();
		const phone_number = form_data.get('phone')?.toString();
		const role = form_data.get('role')?.toString();
		const trading_point = form_data.get('trading_point')?.toString();

		const { error } = await supabase
			.from('staff')
			.update({
				first_name: first_name,
				last_name: last_name,
				middle_name: middle_name,
				phone_number: phone_number,
				role_id: role || undefined,
				trading_point_id: trading_point || undefined
			})
			.eq('id', id);

		if (error) {
			return { success: false, message: error.message };
		} else {
			return { success: true, message: 'updated' };
		}
	}
};
