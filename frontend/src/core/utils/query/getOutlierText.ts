import axios from "axios";

async function retrieveOutlierText(url: string) {
  try {
    const response = await axios.get(url);
    if (response.status === 200) {
      const text = response.data.rules.join("\n");
      return text;
    } else {
      console.error("Failed to retrieve outlier text");
    }
  } catch (error) {
    console.error("Error retrieving outlier text:", error);
  }
}

export async function getOutlierText(
  sessionId: string,
  getUrl: (id: string) => string,
) {
  const url = getUrl(sessionId);
  return await retrieveOutlierText(url);
}
