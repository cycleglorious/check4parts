import Worker from '$lib/utils/workers/TransfromFileWorker.ts?worker';

export type MappedHeader = {
  name: string;
  value: string;
  type: string;
  header: string;
  aliases?: string[];
};

export interface TransformedItem {
  brand: string;
  article: string;
  price: number;
  description: string;
  provider_id: string;
  rests: {
    [warehouseId: string]: number | string;
  };
}

export type WorkerMessage =
  | { type: 'startUpload'; data: { data: any[]; mappedHeaders: MappedHeader[]; providerId: string; companyId: string; authToken: string; } }
  | { type: 'progress'; payload: { state: "transforming" | "hash" }; }
  | { type: 'complete'; payload: { transformedData: TransformedItem[]; hash: string }; }
  | { type: 'error'; payload: { message: string }; };


export async function StartTransformFileWorker(
  fileData: any[],
  mappedHeaders: MappedHeader[],
  providerId: string,
  companyId: string,
  authToken: string,
  onProgress: (progress: { state: "transforming" | "hash" }) => void
): Promise<{ transformedData: TransformedItem[]; hash: string }> {
  return new Promise((resolve, reject) => {
    const worker = new Worker();

    worker.onmessage = (event: MessageEvent<WorkerMessage>) => {
      const message = event.data;

      switch (message.type) {
        case 'progress':
          console.log(`Прогрес воркера: ${message.payload.state}`);
          onProgress(message.payload);
          break;
        case 'complete':
          console.log('Воркер завершив роботу:', message.payload);
          worker.terminate(); // Завершити воркер після завершення роботи
          resolve(message.payload);
          break;
        case 'error':
          console.error('Помилка воркера:', message.payload.message);
          worker.terminate(); // Завершити воркер у випадку помилки
          reject(new Error(message.payload.message));
          break;
        default:
          console.warn('Отримано невідоме повідомлення від воркера:', message);
      }
    };

    // Обробник помилок воркера
    worker.onerror = (error: ErrorEvent) => {
      console.error('Загальна помилка воркера:', error);
      worker.terminate();
      reject(new Error(`Помилка веб-воркера: ${error.message}`));
    };

    // Відправка початкового повідомлення воркеру для запуску трансформації
    worker.postMessage({
      type: 'startUpload',
      data: {
        data: fileData,
        mappedHeaders: mappedHeaders,
        providerId: providerId,
        companyId: companyId,
        authToken: authToken,
      },
    } as WorkerMessage);
  });
}

