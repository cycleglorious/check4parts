import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals: { supabasePrices, supabase } }) => {

  const { data: staff, error: staffError } = await supabase
    .from('staff')
    .select('user_id, first_name, last_name, email')
  
  console.log({ staff, staffError });

  const { data: price_history, error } = await supabasePrices
    .from('price_history')
    .select("*,providers(*)")
    .order("status", { ascending: false })
    .order("created_at", { ascending: false })

  const staffMap = new Map(staff!.map(employee => [employee.user_id, employee]));

  // Об'єднуємо дані
  const enrichedPriceHistory = price_history!.map(priceEntry => ({
    ...priceEntry,
    // Додаємо інформацію про співробітника
    user: staffMap.get(priceEntry.user_id) || null,
    // Додаємо ім'я постачальника з пов'язаної таблиці
    provider_name: priceEntry.providers?.name || null
  }));

  return {
    price_history: enrichedPriceHistory ?? [],
    error: error
  };
};

