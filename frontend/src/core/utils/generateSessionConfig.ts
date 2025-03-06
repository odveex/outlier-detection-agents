import { convertCsvToJsonDict, JsonDict } from "./covertCSVFile";

export type SessionConfig = {
  data_algorithm: string;
  rules_algorithm: string;
  expert_text: string;
  json_dict: JsonDict;
};

export const generateSessionConfig = (
  rules_algorithm: string,
  data_algorithm: string,
  expert_text: string,
  csvFile: string,
): SessionConfig => {
  return {
    data_algorithm,
    rules_algorithm,
    expert_text: expert_text !== "" ? expert_text : "Sample expert information",
    json_dict: convertCsvToJsonDict(csvFile),
  };
};
