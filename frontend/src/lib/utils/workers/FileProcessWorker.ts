/// <reference lib="webworker" />
import * as XLSX from 'xlsx';

self.onmessage = async (event) => {
  const { fileBuffer, fileName, startFrom, previewRowsCount = 5, startPreviewFrom = 0 } = event.data as {
    fileBuffer: ArrayBuffer;
    fileName: string;
    startFrom: number; // 0-based index for the first data row (as per original logic)
    previewRowsCount?: number;
    startPreviewFrom?: number; // 0-based index for preview start in the *original* file rows
  };

  // --- Input Validation ---
  // Reverted startFrom validation to original: must be non-negative
  if (!Number.isInteger(startFrom) || startFrom < 0) {
    self.postMessage({ error: "Невірний параметр startFrom: має бути невід'ємним цілим числом." });
    return;
  }
  if (!Number.isInteger(previewRowsCount) || previewRowsCount < 0) {
    self.postMessage({ error: "Невірний параметр previewRowsCount: має бути невід'ємним цілим числом." });
    return;
  }
  if (!Number.isInteger(startPreviewFrom) || startPreviewFrom < 0) {
    self.postMessage({ error: "Невірний параметр startPreviewFrom: має бути невід'ємним цілим числом." });
    return;
  }

  try {
    self.postMessage({ type: "progress", message: "Початок обробки файлу...", percentage: 5 });

    let workbook: XLSX.WorkBook;
    let json: any[][]; // Will store data processed by XLSX.js with header: 1

    // --- File Type Detection and Parsing ---
    if (fileName.toLowerCase().endsWith('.csv') || fileName.toLowerCase().endsWith('.txt')) {
      const csvString = new TextDecoder('utf-8').decode(fileBuffer);
      const delimiters = [',', ';', '\t', '|'];
      const sample = csvString.substring(0, Math.min(csvString.length, 5000));
      let bestDelim = ',';
      let maxCount = 0;

      for (const delim of delimiters) {
        const count = sample.split(delim).length;
        if (count > maxCount) {
          maxCount = count;
          bestDelim = delim;
        }
      }

      self.postMessage({ type: "progress", message: `Визначено розділювач: '${bestDelim}', читання файлу...`, percentage: 20 });

      workbook = XLSX.read(csvString, {
        type: 'string',
        FS: bestDelim,
        sheetStubs: false,
        codepage: 65001, // UTF-8 codepage
      });
    } else {
      self.postMessage({ type: "progress", message: "Читання файлу Excel...", percentage: 20 });
      workbook = XLSX.read(fileBuffer, { type: 'array' });
    }

    // --- Sheet Selection and Data Extraction ---
    if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
      self.postMessage({ error: "Робоча книга не містить аркушів." });
      return;
    }

    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];

    if (!sheet) {
      self.postMessage({ error: `Аркуш '${sheetName}' не знайдено або порожній.` });
      return;
    }

    self.postMessage({ type: "progress", message: "Конвертація даних аркуша в JSON...", percentage: 50 });
    // Reverted to header: 1, so XLSX.js uses the first row as headers and returns data from the second row.
    // The 'json' array will contain data rows, with the first row of the original sheet implicitly used as headers.
    json = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: "" });

    if (json.length === 0) {
      self.postMessage({ error: "Файл не містить даних." });
      return;
    }

    // Headers are now derived as numeric indices, as per the original request.
    // This assumes the frontend will map these numeric headers to actual column names.
    const headers = json[0].map((_, idx) => idx.toString());

    console.log("Headers detected:", headers);

    // --- Reusable function to map a row array to an object with numeric headers ---
    const mapRowToObj = (row: any[]) => {
      const obj: { [key: string]: string } = {};
      for (let i = 0; i < headers.length; i++) {
        obj[headers[i]] = row[i]?.toString() || "";
      }
      return obj;
    };

    // --- Preview Data ---
    self.postMessage({ type: "progress", message: "Генерація попереднього перегляду...", percentage: 70 });

    // Slice from json directly, which already has the first row (headers) removed by header: 1
    const previewRows = json.slice(startPreviewFrom, previewRowsCount + startPreviewFrom);
    const previewData = previewRows.map(mapRowToObj);

    // Send the numeric headers along with the preview data
    self.postMessage({ type: "preview", previewData, headers });

    // --- Full Data (Single Transfer) ---
    self.postMessage({ type: "progress", message: "Підготовка повних даних...", percentage: 80 });

    // Slice from json directly, which already has the first row (headers) removed by header: 1
    const fileData = json.slice(startFrom).map(mapRowToObj);

    self.postMessage({ type: "full", fileData });

    self.postMessage({ type: "progress", message: "Обробка файлу завершена.", percentage: 100 });

  } catch (err: any) {
    console.error("Помилка в Web Worker:", err);
    self.postMessage({ error: `Помилка при обробці файлу: ${err.message || "Невідома помилка"}` });
  }
};
