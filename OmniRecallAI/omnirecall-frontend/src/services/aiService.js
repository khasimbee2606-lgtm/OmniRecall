import API from "./api";

export const getAIInsights = async () => {
  const response = await API.get("/insights");
  return response.data;
};
