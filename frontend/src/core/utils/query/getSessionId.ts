import axios from "axios";
import { REGISTER_SESSION_URL } from "../../model/urls";
import { generateSessionConfig, SessionConfig } from "../generateSessionConfig";

async function registerSession(config: SessionConfig) {
  try {
    const response = await axios.post(
      REGISTER_SESSION_URL,
      JSON.stringify(config),
      {
        headers: {
          "Content-Type": "application/json",
        },
      },
    );
    if (response.data.status === "success") {
      const sessionId = response.data.task_id;
      return sessionId as string;
    } else {
      console.error("Failed to register session");
      return null;
    }
  } catch (error) {
    console.error("Error registering session:", error);
    return null;
  }
}

export async function getSessionId(
  rulesAlgorithm: string,
  outlierDetectionAlgorithm: string,
  expertInfo: string,
  csvFile: string,
) {
  const sessionConfig = generateSessionConfig(
    rulesAlgorithm,
    outlierDetectionAlgorithm,
    expertInfo,
    csvFile,
  );
  return await registerSession(sessionConfig);
}
