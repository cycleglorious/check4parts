import type { PageServerLoad } from "./$types";
import { fail } from "@sveltejs/kit";
import type { Actions } from "./$types";
import jwt from 'jsonwebtoken';

export const load: PageServerLoad = async ({ locals: { supabasePrices: supabase, session } }) => {
  const [providersResponse, warehousesResponse] = await Promise.all([
    supabase.from("providers").select("*").order("name"),
    supabase.from("warehouses").select("*").order("name"),
  ]);

  if (providersResponse.error) {
    console.error("Error fetching providers:", providersResponse.error);
    throw fail(500, { message: "Failed to load providers." });
  }

  if (warehousesResponse.error) {
    console.error("Error fetching warehouses:", warehousesResponse.error);
    throw fail(500, { message: "Failed to load warehouses." });
  }

  return {
    providers: providersResponse.data,
    warehouses: warehousesResponse.data,
  };
};

// Функція з обмеженням паралельності
async function mapWithConcurrency<T, R>(
  items: T[],
  fn: (item: T, index: number) => Promise<R>,
  concurrency = 5
): Promise<R[]> {
  const results: R[] = new Array(items.length); // Pre-allocate array for direct assignment
  const executing: Set<Promise<void>> = new Set(); // Use a Set for more efficient removal

  for (let i = 0; i < items.length; i++) {
    const itemPromise = fn(items[i], i).then((res) => {
      results[i] = res;
      executing.delete(itemPromise); // Remove the promise when it resolves
    });

    executing.add(itemPromise);

    if (executing.size >= concurrency) {
      await Promise.race(executing);
    }
  }

  await Promise.all(executing);
  return results;
}

export const actions: Actions = {
  processChunks: async ({ request, locals: { supabasePrices: supabase, user, session } }) => {
    const formData = await request.formData();
    const processedData = formData.getAll("processedData").toString().split(",");
    const providerID = formData.get("provider_id")?.toString() || "0";
    const decodedToken = jwt.decode(session?.access_token || '');
    const company_id = typeof decodedToken === 'object' && decodedToken !== null ? decodedToken.company_id : undefined;

    if (!user?.id) {
      return fail(401, { success: false, message: "❌ Unauthorized: User ID is missing." });
    }


    const createdAt = new Date().toISOString();
    const uploadedChunksId = processedData[0]?.split("/")[1] || "unknown";

    // 1. Створюємо запис у price_history зі статусом 'uploading'
    const { data: historyRecord, error: historyCreateError } = await supabase
      .from("price_history")
      .insert({
        provider_id: providerID,
        created_at: createdAt,
        status: "uploading",
        chunk_id: uploadedChunksId,
      })
      .select()
      .single();

    if (historyCreateError || !historyRecord?.id) {
      console.error("❌ Failed to create price_history:", {historyCreateError});
      return fail(500, { success: false, message: "❌ Failed to create price_history record" });
    }

    const historyId = historyRecord.id;

    // 2. Завантаження та імпорт по чанках
    const chunkResults = await mapWithConcurrency(
      processedData,
      async (chunkPath, i) => {
        try {
          const { data: fileData, error: downloadError } = await supabase.storage
            .from("prices")
            .download(chunkPath);

          if (downloadError || !fileData) {
            throw new Error(`Download failed for ${chunkPath}: ${downloadError?.message || "Unknown error"}`);
          }

          const parsedData = JSON.parse(await fileData.text());

      
          const { data: result, error: rpcError } = await supabase.rpc(
            "import_prices_from_json",
            {
              p_json_data: parsedData,
              p_provider_id: providerID,
              p_history_id: historyId,
              p_company_id: company_id,
            }
          );

          if (rpcError) {
            throw new Error(`RPC call failed for ${chunkPath}: ${rpcError.message}`);
          }

          console.log(`✅ Chunk ${chunkPath} processed successfully:`, result);
          return { success: true, result };
        } catch (error: any) {
          console.error(`❌ Error processing chunk ${chunkPath}:`, error.message);
          return {
            success: false,
            error: error?.message || "An unknown error occurred",
            chunk: chunkPath,
          };
        }
      },
      10
    );

    const successfulChunks = chunkResults.filter((r) => r.success);
    const failedChunks = chunkResults.filter((r) => !r.success);

    const aggregated = successfulChunks.reduce((acc, item: any) => {
      const r = item.result || {};
      return {
        inserted: acc.inserted + (r.inserted_count || 0),
        missingBrands: acc.missingBrands.concat(r.missing_brands || []),
        missingArticles: acc.missingArticles.concat(r.missing_articles || []),
      };
    }, {
      inserted: 0,
      missingBrands: [],
      missingArticles: [],
    });

    // 3. Очищення старих цін
    const { error: cleanupError } = await supabase.rpc("cleanup_old_prices", {
      p_provider_id: providerID,
      p_created_at: createdAt,
      p_company_id: company_id,
    });

    if (cleanupError) {
      console.warn("⚠️ Cleanup old prices error:", cleanupError);
    } else {
      console.log("✅ Old prices cleaned up successfully.");
    }

    // 4. Оновлюємо статуси в price_history
    const [{ error: actualError }, { error: deletedError }] = await Promise.all([
      supabase.from("price_history")
        .update({ status: "actual" })
        .eq("id", historyId),

      supabase.from("price_history")
        .update({ status: "deleted" })
        .neq("id", historyId)
        .eq("provider_id", providerID)
    ]);

    if (actualError) console.warn("⚠️ Failed to mark current history as actual:", actualError.message);
    if (deletedError) console.warn("⚠️ Failed to mark old histories as deleted:", deletedError.message);

    // 5. Підрахунок актуальних записів
    const { count, error: countError } = await supabase
      .from("prices")
      .select("*", { count: "exact", head: true })
      .eq("provider_id", providerID)

    console.log(`✅ Total current prices for provider ${providerID}:`, count);

    // 6. Повернення результату (без змін)
    return {
      success: true,
      stats: {
        processed: processedData.length,
        succeeded: successfulChunks.length,
        inserted: aggregated.inserted,
        remaining: count || 0,
        failed: failedChunks.length,
      },
      missing: {
        brands: Array.from(new Set(aggregated.missingBrands)),
        articles: Array.from(new Set(aggregated.missingArticles)),
        articlesFile: null,
      },
      errors: failedChunks.map((f) => ({ chunk: f.chunk, error: f.error })),
      chunks: chunkResults.map((r, i) => ({
        index: i + 1,
        path: processedData[i],
        success: r.success,
        error: r.error || null,
      })),
    };
  },
};
