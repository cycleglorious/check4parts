import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabase } }) => {
  const { data: { user } } = await supabase.auth.getUser()
  const { data: staff } = await supabase
    .from('staff')
    .select('*,trading_points(*),roles(*)')
    .eq('user_id', user?.id)
    .single();
  return {
    user: user ?? null,
    staff: staff ?? null,
  }
};