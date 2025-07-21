// src/lib/utils/supabaseUploadManager.ts
import type { TransformedItem } from "./TransformFileData";
import type { SupabaseClient } from "@supabase/supabase-js";
import Worker from '$lib/utils/workers/SupabaseUploadWorker.ts?worker';


export type AppSettings = {
  startFrom: number;
  chunkSize: number;
  concurrencyLimit: number;
};

// Define the messages that can be sent to and received from the worker
export type WorkerMessage =
  | { type: 'startUpload'; data: { data: TransformedItem[]; providerId: string; settings: AppSettings; supabaseUrl: string; supabaseAnonKey: string; }; }
  | { type: 'progress'; payload: { uploadedCount: number; totalCount: number; percentage: number; message: string }; }
  | { type: 'complete'; }
  | { type: 'error'; payload: { message: string }; };

let uploadWorker: Worker | null = null;
let currentOnProgress: ((progress: { uploadedCount: number; totalCount: number; percentage: number; message: string }) => void) | undefined;
let currentReject: ((reason?: any) => void) | undefined;

export async function startWorkerUpload(
  data: TransformedItem[],
  providerId: string,
  settings: AppSettings,
  authToken: string,
  onProgress?: (progress: { uploadedCount: number; totalCount: number; percentage: number; message: string }) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    // Terminate existing worker if any, to ensure a clean slate
    if (uploadWorker) {
      uploadWorker.terminate();
      uploadWorker = null;
    }

    uploadWorker = new Worker();

    currentOnProgress = onProgress;
    currentReject = reject; // Store reject for error handling

    uploadWorker.onmessage = (event: MessageEvent<WorkerMessage>) => {
      const { type } = event.data;
      const payload = (event.data as any).payload; // Safely extract payload if it exists
      switch (type) {
        case 'progress':
          if (payload) {
            currentOnProgress?.(payload);
          }
          break;
        case 'complete':
          currentOnProgress?.({ uploadedCount: payload?.totalCount || 0, totalCount: payload?.totalCount || 0, percentage: 100, message: 'Завантаження завершено!' });
          uploadWorker?.terminate();
          uploadWorker = null;
          resolve();
          break;
        case 'error':
          currentOnProgress?.({ uploadedCount: payload?.uploadedCount || 0, totalCount: payload?.totalCount || 0, percentage: payload?.percentage || 0, message: `Помилка: ${payload?.message || 'Unknown error'}` });
          uploadWorker?.terminate();
          uploadWorker = null;
          reject(new Error(payload?.message || 'Unknown error'));
          break;
      }
    };

    uploadWorker.onerror = (error: ErrorEvent) => {
      console.error('Worker error:', error);
      currentOnProgress?.({ uploadedCount: 0, totalCount: 0, percentage: 0, message: `Критична помилка воркера: ${error.message}` });
      uploadWorker?.terminate();
      uploadWorker = null;
      reject(new Error(`Критична помилка воркера: ${error.message}`));
    };

    // Get Supabase URL and Key from the client instance (assuming it was created using PUBLIC env vars)
    // You might need a more robust way to get these if your client setup is different.


    // Send the data and configuration to the worker
    uploadWorker.postMessage({
      type: 'startUpload',
      data: {
        data: data,
        providerId,
        settings: JSON.parse(JSON.stringify(settings)),
        authToken
      },
    });
  });
}

export function terminateWorkerUpload() {
  if (uploadWorker) {
    uploadWorker.terminate();
    uploadWorker = null;
    currentOnProgress?.({ uploadedCount: 0, totalCount: 0, percentage: 0, message: 'Завантаження скасовано.' });
    currentReject?.(new Error('Upload cancelled by user.'));
  }
}