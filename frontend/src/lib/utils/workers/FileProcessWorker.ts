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
    self.postMessage({ error: "Невірний параметр startFrom" });
    return;
  }

  try {
    let workbook;
    let json: any[][];

    if (fileName.toLowerCase().endsWith('.csv') || fileName.toLowerCase().endsWith('.txt')) {
      const csvString = new TextDecoder('utf-8').decode(fileBuffer);
      const delimiters = [',', ';', '\t', '|'];
      const sample = csvString.substring(0, 1000);
      let bestDelim = ',';
      let maxCount = 0;

      for (const delim of delimiters) {
        const count = sample.split(delim).length;
        if (count > maxCount) {
          maxCount = count;
          bestDelim = delim;
        }
      }

      workbook = XLSX.read(csvString, {
        type: 'string',
        FS: bestDelim,
        sheetStubs: false,
        codepage: 65001,
      });
    } else {
      workbook = XLSX.read(fileBuffer, { type: 'array' });
    }

    const sheet = workbook.Sheets[workbook.SheetNames[0]];
    json = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: "" });

    if (json.length === 0) {
      self.postMessage({ error: "Файл не містить даних" });
      return;
    }

    const headers = json[0].map((_, idx) => idx.toString());

    console.log("Headers detected:", headers);
    // 🔍 Preview (перші 5 рядків як об'єкти з індексами)
    const previewRows = json.slice(startPreviewFrom, previewRowsCount + startPreviewFrom);
    const previewData = previewRows.map(row =>
      Object.fromEntries(headers.map((h, i) => [h, row[i]?.toString() || ""]))
    );

    self.postMessage({ type: "preview", previewData, headers });

    // 📦 Повні дані
    const fileData = json.slice(startFrom).map(row =>
      Object.fromEntries(headers.map((h, i) => [h, row[i]?.toString() || ""]))
    );

    self.postMessage({ type: "full", fileData });
  } catch (err: any) {
    self.postMessage({ error: err.message || "Помилка при обробці" });
  }
};
