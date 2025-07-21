import Worker from '$lib/utils/workers/FileProcessWorker.ts?worker';
import { on } from 'svelte/events';

export const processFile = async (
  files: FileList,
  startFrom: number,
  previewRows: number = 5,
  startPreviewFrom: number = 0,
  {
    onPreview,
    onFull,
    onProgress,
  }: {
    onPreview: (data: { previewData: any[] }) => void,
    onFull: (data: { fileData: any[], fileName: string, fileType: string, fileSize: number }) => void
    onProgress: (data: { message: string, percentage: number }) => void,
  }
) => {
  if (!files?.[0]) return;
  const file = files[0];


  return new Promise<void>((resolve, reject) => {
    const worker = new Worker();
    console.log("Worker initialized for file processing");
    worker.onmessage = (e) => {
      const { type, error, previewData, fileData } = e.data;

      if (error) {
        worker.terminate();
        reject(new Error(error));
        return;
      }
      if (type === "progress") {
        onProgress({ message: e.data.message, percentage: e.data.percentage });
        console.log("Progress update:", e.data.message, "Percentage:", e.data.percentage);
      } else if (type === "preview") {
        onPreview({ previewData });
        console.log("Preview data received:", previewData.length, "rows");
      } else if (type === "full") {
        onFull({
          fileData,
          fileName: file.name,
          fileType: file.type,
          fileSize: file.size,
        });
        console.log("Full data received:", fileData.length, "rows");
        console.log(fileData.slice(0, 5)); // Log first 5 rows for debugging
        onProgress({ message: "Файл обролено", percentage: 100 });
        worker.terminate();
        resolve();
      }
    };

    worker.onerror = (err) => {
      worker.terminate();
      reject(err);
    };

    // ✅ передаємо startFrom
    worker.postMessage({ file: file, fileName: file.name, startFrom, previewRows, startPreviewFrom });
  });
};
