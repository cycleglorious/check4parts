// src/lib/utils/supabaseUploadWorker.ts
import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { AppSettings, PriceRowForDB, WorkerMessage } from '../loader/SupabaseUpload';
import type { TransformedItem } from '../loader/TransformFile.svelte';

// Function to send messages back to the main thread
function postMessageToMain(message: WorkerMessage) {
	self.postMessage(message);
}

// The core upload logic, now inside the worker
async function uploadPricesToSupabaseInWorker(
	data: TransformedItem[],
	hash: string,
	providerId: string,
	settings: AppSettings,
	supabase: SupabaseClient
): Promise<void> {
	const totalCount = data.length;
	let uploadedCount = 0;
	const chunkSize = settings.chunkSize;
	const concurrencyLimit = settings.concurrencyLimit || 5;
	let historyId: string | null = null;
	let historyCreatedAt: string | null = null;

	try {
		postMessageToMain({
			type: 'progress',
			payload: { uploadedCount: 0, totalCount, percentage: 0, message: 'Початок завантаження...' }
		});
		const { count: isHashExists, error: hashCheckError } = await supabase
			.from('price_history')
			.select('id', { count: 'exact' })
			.eq('hash', hash)
			.eq('provider_id', providerId)
			.eq('status', 'actual');

		if (hashCheckError) {
			throw new Error(
				`Помилка перевірки історії цін: ${hashCheckError.message}, ${JSON.stringify(hashCheckError)}, ${providerId}`
			);
		}
		if (isHashExists! > 0) {
			postMessageToMain({
				type: 'error',
				payload: { message: `Дані з таким хешем вже існують для цього постачальника.` }
			});
			return;
		}

		postMessageToMain({
			type: 'progress',
			payload: {
				uploadedCount: 0,
				totalCount,
				percentage: 0,
				message: 'Створення запису історії завантаження...'
			}
		});
		const { data: historyData, error: historyError } = await supabase
			.from('price_history')
			.insert({
				provider_id: providerId,
				status: 'uploading',
				hash: hash
			})
			.select('id, created_at')
			.single();

		if (historyError) {
			throw new Error(
				`Помилка створення історії цін: ${historyError.message}, ${JSON.stringify(historyError)}, ${providerId}`
			);
		}
		historyId = historyData.id;
		historyCreatedAt = historyData.created_at;

		postMessageToMain({
			type: 'progress',
			payload: {
				uploadedCount: 0,
				totalCount,
				percentage: 5,
				message: 'Початок завантаження даних...'
			}
		});

		// Create an array of promises, limiting concurrency
		const allChunkPromises: Promise<void>[] = [];
		for (let i = 0; i < totalCount; i += chunkSize) {
			const chunkToProcess = data.slice(i, i + chunkSize);
			if (chunkToProcess.length > 0) {
				allChunkPromises.push(
					(async (currentChunk, currentChunkIndex) => {
						// Wrap in an IIFE to capture chunk context
						const rowsToInsert: PriceRowForDB[] = currentChunk.map((item) => ({
							brand: item.brand,
							article: item.article,
							price: item.price,
							description: item.description === '' ? null : item.description,
							provider_id: providerId,
							rests: item.rests,
							history_id: historyId!
						}));

						try {
							const { error } = await supabase.from('prices').insert(rowsToInsert);
							if (error) {
								const { error: updateError } = await supabase
									.from('price_history')
									.update({ status: 'failed' })
									.eq('id', historyId);
								if (updateError) {
									console.warn(
										`Помилка оновлення статусу історії цін (${historyId}): ${updateError.message}`
									);
								}
								throw new Error(
									`Помилка завантаження даних (пакет ${Math.floor(currentChunkIndex / chunkSize) + 1}): ${JSON.stringify(error)}`
								);
							}
							// Atomically update uploadedCount and send progress
							uploadedCount += currentChunk.length;
							const percentage = Math.min(95, (uploadedCount / totalCount) * 90 + 5);
							postMessageToMain({
								type: 'progress',
								payload: {
									uploadedCount,
									totalCount,
									percentage,
									message: `Завантаження... ${uploadedCount} з ${totalCount} записів.`
								}
							});
						} catch (e: any) {
							console.error('Error during chunk upload:', e);
							throw e; // Re-throw to be caught by Promise.all
						}
					})(chunkToProcess, i) // Pass chunk and its starting index
				);
			}
		}

		// Use a queue to manage concurrency
		const uploadQueue = async (tasks: Promise<void>[], limit: number) => {
			const results = [];
			const running: Promise<void>[] = [];

			for (const task of tasks) {
				if (running.length >= limit) {
					await Promise.race(running);
				}
				const p = task.then((res) => {
					running.splice(running.indexOf(p), 1);
					return res;
				});
				running.push(p);
				results.push(p);
			}
			return Promise.all(results);
		};

		await uploadQueue(allChunkPromises, concurrencyLimit);

		// 3. Update price_history status to 'actual'
		if (historyId) {
			postMessageToMain({
				type: 'progress',
				payload: {
					uploadedCount: totalCount,
					totalCount,
					percentage: 95,
					message: 'Завершення завантаження...'
				}
			});
			const { error: updateError } = await supabase
				.from('price_history')
				.update({ status: 'actual' })
				.eq('id', historyId);
			if (updateError) {
				console.warn(
					`Помилка оновлення статусу історії цін (${historyId}): ${updateError.message}`
				);
			}
		}

		// 4. Delete old prices via RPC
		if (historyId && historyCreatedAt) {
			postMessageToMain({
				type: 'progress',
				payload: {
					uploadedCount: totalCount,
					totalCount,
					percentage: 98,
					message: 'Видалення старих записів цін...'
				}
			});
			const { data: deletedCount, error: deleteError } = await supabase.rpc('cleanup_old_prices', {
				p_provider_id: providerId,
				p_created_at: historyCreatedAt
			});

			if (deleteError) {
				console.error(`Помилка видалення старих цін: ${deleteError.message}`);
			} else {
				console.log(`Видалено ${deletedCount} старих записів цін.`);
			}
		}

		postMessageToMain({ type: 'complete', payload: { totalCount } });
	} catch (error: any) {
		console.error('Upload process failed in worker:', error);
		// Ensure history status is updated to 'failed' on error
		if (historyId) {
			await supabase.from('price_history').update({ status: 'failed' }).eq('id', historyId);
		}
		postMessageToMain({
			type: 'error',
			payload: {
				message: error.message,
				uploadedCount,
				totalCount,
				percentage: Math.min(95, (uploadedCount / totalCount) * 90 + 5)
			}
		});
	}
}

// Listen for messages from the main thread
self.onmessage = (event: MessageEvent<WorkerMessage>) => {
	if (event.data.type === 'startUpload') {
		const { data, providerId, settings, authToken, hash } = event.data.data;

		// Initialize Supabase client within the worker context

		uploadPricesToSupabaseInWorker(
			data,
			hash,
			providerId,
			settings,
			createClient(event.data.data.supabaseUrl, event.data.data.supabaseAnonKey, {
				global: {
					headers: {
						Authorization: `Bearer ${authToken}`
					}
				}
			})
		);
	}
};
