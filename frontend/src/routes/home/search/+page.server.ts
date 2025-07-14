// import { createClient } from '@supabase/supabase-js'; // ЦЕЙ РЯДОК НЕ ПОТРІБЕН
// import { SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY } from '$env/static/private'; // ЦЕЙ РЯДОК НЕ ПОТРІБЕН
// const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY); // ЦЕЙ РЯДОК НЕ ПОТРІБЕН

import type { PageServerLoad } from './$types';

// Змінено: отримуємо supabase з locals
export const load: PageServerLoad = async ({ url, locals: { supabaseTecdoc: supabase } }) => {
  const searchQuery = url.searchParams.get('q');

  let partsPromise: Promise<any[]>;

  if (searchQuery) {
    partsPromise = (async () => {
      const { data: articlesData, error: articlesError } = await supabase
        .from('articles')
        .select(
          `
          id,
          "DataSupplierArticleNumber",
          "NormalizedDescription",
          "Description",
          suppliers (
            id,
            "MatchCode",
            "Description"
          )
        `
        )
        .eq('DataSupplierArticleNumber', searchQuery)
        .limit(50);

      if (articlesError) {
        console.error('Error fetching articles for search:', articlesError);
        throw new Error('Failed to perform search: ' + articlesError.message);
      }

      if (articlesData) {
        return articlesData.map(article => ({
          name: article.NormalizedDescription || 'Без опису',
          description: article.Description || article.NormalizedDescription || 'Без опису',
          brand: article.suppliers?.MatchCode || 'Невідомий бренд',
          details: [],
          id: article.DataSupplierArticleNumber || 'N/A',
          code: article.id?.toString() || '',
          image: '/image 7.png',
          rests: []
        }));
      }
      return [];
    })();
  } else {
    partsPromise = Promise.resolve([]);
  }


  return {
    searchQuery,
    parts: partsPromise
  };
};