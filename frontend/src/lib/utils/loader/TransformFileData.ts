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
    [warehouseId: string]: number;
  };
}

export async function transformFileData(
  fileData: any[],
  mappedHeaders: MappedHeader[],
  selectedProvider: string
): Promise<TransformedItem[]> { // Function now returns a Promise
  const transformedData: TransformedItem[] = [];

  // Create a quick lookup for props and rests from mappedHeaders
  const propMappings = new Map<string, string>();
  const restMappings = new Map<string, string>();

  mappedHeaders.forEach(mh => {
    if (mh.header !== "") {
      if (mh.type === 'prop') {
        propMappings.set(mh.value, String(mh.header));
      } else if (mh.type === 'rests') {
        restMappings.set(mh.value, String(mh.header));
      }
    }
  });

  await new Promise(resolve => setTimeout(resolve, 0));
  for (const row of fileData) {
    const newItem: TransformedItem = {
      brand: '',
      article: '',
      price: 0,
      description: '',
      provider_id: selectedProvider,
      rests: {}
    };

    newItem.brand = String(row[propMappings.get('brand') ?? ''] || '');
    newItem.article = String(row[propMappings.get('article') ?? ''] || '');
    newItem.description = String(row[propMappings.get('description') ?? ''] || '');

    const priceStr = String(row[propMappings.get('price') ?? ''] || '').replace(',', '.');
    newItem.price = parseFloat(priceStr) || 0;

    for (const [warehouseId, fileColumnIndex] of restMappings.entries()) {
      const restValue = String(row[fileColumnIndex] || '');
      newItem.rests[warehouseId] = parseInt(restValue, 10) || 0;
    }

    transformedData.push(newItem);
  }

  return transformedData;
}