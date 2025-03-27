import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ depends, locals: { supabase } }) => {
	depends('supabase:db:staff');
	const { data: staff } = await supabase.from('staff').select('*,companies(*)').order('id');
	console.log(staff);
	return { staff: staff ?? [] };
};
