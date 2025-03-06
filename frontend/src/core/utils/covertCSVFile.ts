export type JsonDict = {
  [key: string]: { [index: number]: number | string | null };
};

export function convertCsvToJsonDict(csvText: string): JsonDict {
  const lines = csvText.trim().split("\n");
  const headers = lines[0].split(",").map((header) => header.trim());
  const result: JsonDict = {};

  headers.forEach((header) => {
    result[header] = {};
  });

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(",");

    headers.forEach((header, index) => {
      let value = values[index]?.trim();
      if (value?.startsWith('"')) {
        value = value.slice(1);
      }
      const parsedValue =
        value === "" || value === undefined
          ? null
          : isNaN(parseFloat(value))
            ? value
            : parseFloat(value);
      result[header][i - 1] = parsedValue;
    });
  }

  return result;
}
