/// <reference lib="webworker" />
import * as XLSX from 'xlsx';

self.onmessage = async (event) => {
  const { fileBuffer, fileName, startFrom, previewRowsCount = 5, startPreviewFrom = 0 } = event.data as {
    fileBuffer: ArrayBuffer;
    fileName: string;
    startFrom: number;
    previewRowsCount?: number;
    startPreviewFrom?: number;
  };

  if (!Number.isInteger(startFrom) || startFrom < 0) {
    self.postMessage({ type: "error", error: "Невірний параметр startFrom: має бути невід'ємним цілим числом." });
    return;
  }
  if (!Number.isInteger(previewRowsCount) || previewRowsCount < 0) {
    self.postMessage({ type: "error", error: "Невірний параметр previewRowsCount: має бути невід'ємним цілим числом." });
    return;
  }
  if (!Number.isInteger(startPreviewFrom) || startPreviewFrom < 0) {
    self.postMessage({ type: "error", error: "Невірний параметр startPreviewFrom: має бути невід'ємним цілим числом." });
    return;
  }

  try {
    self.postMessage({ type: "progress", message: "Початок обробки файлу...", percentage: 5 });

    let workbook: XLSX.WorkBook;
    let json: any[][];

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

      self.postMessage({ type: "progress", message: `Читання файлу...`, percentage: 20 });

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
      self.postMessage({ type: "error", error: "Робоча книга не містить аркушів." });
      return;
    }

    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];

    if (!sheet) {
      self.postMessage({ type: "error", error: `Аркуш '${sheetName}' не знайдено або порожній.` });
      return;
    }

    self.postMessage({ type: "progress", message: "Конвертація даних...", percentage: 50 });
    json = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: "" });

    if (json.length === 0) {
      self.postMessage({ type: "error", error: "Файл не містить даних." });
      return;
    }

    const headers = json[0].map((_, idx) => idx.toString());
    console.log("Headers detected:", headers);

    const mapRowToObj = (row: any[]) => {
      const obj: { [key: string]: string } = {};
      for (let i = 0; i < headers.length; i++) {
        obj[headers[i]] = row[i]?.toString() || "";
      }
      return obj;
    };

    // --- Preview Data ---
    self.postMessage({ type: "progress", message: "Генерація попереднього перегляду...", percentage: 70 });

    const previewRows = json.slice(startPreviewFrom, previewRowsCount + startPreviewFrom);
    const previewData = previewRows.map(mapRowToObj);

    self.postMessage({ type: "preview", previewData, metadata: { headers, rowCount: previewRows.length } });

    self.postMessage({ type: "progress", message: "Підготовка повних даних...", percentage: 80 });

    const fileData = json.slice(startFrom).map(mapRowToObj);
    self.postMessage({ type: "full", fileData });
    self.postMessage({ type: "progress", message: "Обробка файлу завершена.", percentage: 100 });

  } catch (err: any) {
    console.error("Помилка в Web Worker:", err);
    self.postMessage({ type: "error", error: `Помилка при обробці файлу: ${err.message || "Невідома помилка"}` });
  }
};
