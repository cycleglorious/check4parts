import { createBrowserClient, createServerClient, isBrowser } from '@supabase/ssr';
import {
	PUBLIC_SUPABASE_ANON_KEY,
	PUBLIC_SUPABASE_PRICES_ANON_KEY,
	PUBLIC_SUPABASE_PRICES_URL,
	PUBLIC_SUPABASE_URL
} from '$env/static/public';
import type { LayoutLoad } from './$types';
import { createClient } from '@supabase/supabase-js';
// import { createClient } from '@supabase/supabase-js'; // Цей імпорт більше не потрібен, якщо ви використовуєте тільки @supabase/ssr

export const load: LayoutLoad = async ({ data, depends, fetch }) => {
	/**
	 * Оголошуємо залежність, щоб макет можна було інвалідувати,
	 * наприклад, при оновленні сесії.
	 */
	depends('supabase:auth');

	// Ініціалізація основного клієнта Supabase
	const supabase = isBrowser()
		? createBrowserClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
				global: {
					fetch
				}
			})
		: createServerClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
				global: {
					fetch
				},
				cookies: {
					getAll() {
						return data.cookies;
					}
				}
			});

	/**
	 * Отримуємо сесію з основного клієнта.
	 * Це безпечно використовувати тут, оскільки на клієнті getSession безпечний,
	 * а на сервері він читає сесію з LayoutData.
	 */
	const {
		data: { session }
	} = await supabase.auth.getSession();

	// Ініціалізація клієнта Supabase для цін
	// ВАЖЛИВО: Видалено ручну передачу заголовка Authorization.
	// createBrowserClient та createServerClient автоматично керуватимуть токенами
	// через cookies/local storage, якщо JWT Secret спільний.
	const supabasePrices = isBrowser()
		? createClient(PUBLIC_SUPABASE_PRICES_URL, PUBLIC_SUPABASE_PRICES_ANON_KEY, {
				global: {
					headers: {
						Authorization: `Bearer ${session?.access_token}`
					}
				}
			})
		: createServerClient(PUBLIC_SUPABASE_PRICES_URL, PUBLIC_SUPABASE_PRICES_ANON_KEY, {
				global: {
					headers: {
						Authorization: `Bearer ${session?.access_token}`
					}
				},
				cookies: {
					getAll() {
						return data.cookies;
					}
				}
			});

	const {
		data: { user }
	} = await supabase.auth.getUser();

	return { session, supabase, user, supabasePrices };
};
