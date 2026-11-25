import API from "./api";

export const semanticSearch = async (query) => {
  const response = await API.get(`/search?q=${query}`);
  return response.data;
};
