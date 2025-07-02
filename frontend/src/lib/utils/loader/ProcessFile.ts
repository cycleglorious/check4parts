import Worker from '$lib/utils/workers/FileProcessWorker.ts?worker';

export const processFile = async (
  files: FileList,
  startFrom: number,
  previewRows: number = 5,
  startPreviewFrom: number = 0,
  {
    onPreview,
    onFull,
  }: {
    onPreview: (data: { previewData: any[] }) => void,
    onFull: (data: { fileData: any[], fileName: string, fileType: string, fileSize: number }) => void
  }
) => {
  if (!files?.[0]) return;
  const file = files[0];
  const buffer = await file.arrayBuffer();

  console.log("Processing file:", file.name, "Start from:", startFrom, "Preview rows:", previewRows, "Start preview from:", startPreviewFrom);

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

      if (type === "preview") {
        onPreview({ previewData });
        console.log("Preview data received:", previewData.length, "rows");
      } else if (type === "full") {
        onFull({
          fileData,
          fileName: file.name,
          fileType: file.type,
          fileSize: file.size,
        });
        worker.terminate();
        resolve();
      }
    };

    worker.onerror = (err) => {
      worker.terminate();
      reject(err);
    };

    // ✅ передаємо startFrom
    worker.postMessage({ fileBuffer: buffer, fileName: file.name, startFrom, previewRows, startPreviewFrom});
  });
};
