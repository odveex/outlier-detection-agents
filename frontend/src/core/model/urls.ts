export const REGISTER_SESSION_URL = "http://localhost:8000/register_data/";

export const GET_OUTLIER_TEXT_URL = (id: string) =>
  `http://localhost:8000/tasks/${id}/outliers_from_data`;

export const GET_OUTLIER_IMAGE_URL = (id: string) =>
  `http://localhost:8000/tasks/${id}/outliers_from_data_img`;

export const GET_OUTLIER_TEXT_WITH_EXPERT_URL = (id: string) =>
  `http://localhost:8000/tasks/${id}/outliers_integrated`;

export const GET_OUTLIER_IMAGE_WITH_EXPERT_URL = (id: string) =>
  `http://localhost:8000/tasks/${id}/outliers_integrated_img`;
