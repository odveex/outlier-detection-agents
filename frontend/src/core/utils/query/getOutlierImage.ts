import axios from "axios";

async function retrieveOutlierImage(url: string) {
  try {
    const response = await axios.get(url);

    if (response.status === 200) {
      return response.data.image_url;
    } else {
      console.error("Failed to retrieve outlier image");
    }
  } catch (error) {
    console.error("Error retrieving outlier image:", error);
  }
}

export async function getOutlierImage(
  sessionId: string,
  getUrl: (id: string) => string,
) {
  const url = getUrl(sessionId);
  return await retrieveOutlierImage(url);
}
