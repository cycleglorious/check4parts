/// <reference lib="webworker" />
import { createClient, type Session } from "@supabase/supabase-js";
import { v4 as uuidv4 } from "uuid";

interface TemplateItem {
  value: string;
  header: string;
  type: "prop" | "rests";
}

interface FileRow {
  [key: string]: any;
}

self.onmessage = async (e) => {
  try {
    const { fileData, template, chunkSize = 1000, session, supabaseUrl, supabaseAnonKey } = e.data as {
      fileData: FileRow[];
      template: TemplateItem[];
      chunkSize?: number;
      session: Session | null
      supabaseUrl: string;
      supabaseAnonKey: string;
    };

    console.log({supabaseUrl, supabaseAnonKey});

    const uploadId = uuidv4();
    const uploadedFiles: string[] = [];

    const supabase = createClient(
      supabaseUrl,
      supabaseAnonKey,
      {
        global: {
          headers: {
            Authorization: `Bearer ${session?.access_token}`
          }
        }
      }
    );

    const mappedData = fileData
    .map((row) => {
      const entry: any = {
        brand: "",
        article: "",
        price: 0,
        description: "",
        rests: {}
      };
  
      template.forEach(({ type, value, header }) => {
        const cellRaw = row[header];
        const cellValue =
          typeof cellRaw === "string" ? cellRaw.trim() : String(cellRaw || "0");
  
        if (type === "prop") {
          entry[value] =
            value === "price"
              ? parseFloat(cellValue.replace(",", ".")) || 0
              : cellValue;
        } else if (type === "rests") {
          entry.rests[value] = cellValue;
        }
      });
  
      return entry;
    })
    .filter((entry) => {  
      return (!entry.article || entry.article.trim() === "") ? false : true;
    });
  

    self.postMessage({ type: "mapped" });
    console.log(mappedData.length,  mappedData.length / chunkSize);

    for (let i = 0; i < mappedData.length; i += chunkSize) {
      const chunk = mappedData.slice(i, i + chunkSize);
      const filename = `chunks/${uploadId}/chunk_${Math.floor(i / chunkSize) + 1}.json`;

      let jsonStr: string;
      try {
        jsonStr = JSON.stringify(chunk);
      } catch (err) {
        self.postMessage({ type: "error", error: "Помилка серіалізації JSON" });
        return;
      }

      const file = new File([jsonStr], filename, {
        type: "application/json",
      });

      const { error } = await supabase.storage
        .from("prices")
        .upload(filename, file, {
          contentType: "application/json",
          cacheControl: "3600",
        });

      if (error) {
        self.postMessage({ type: "error", error: error.message });
        return;
      }

      uploadedFiles.push(filename);

      const progressValue = Math.min(
        100,
        Math.round(((i + chunk.length) / mappedData.length) * 100),
      );

      self.postMessage({ type: "progress", value: progressValue });
    }

    self.postMessage({ type: "done", uploadedFiles, uploadId });
  } catch (error: any) {
    self.postMessage({ type: "error", error: error.message || "Невідома помилка" });
  }
};
