import API from "./api";

export const uploadImage = async (formData) => {
  const response = await API.post("/upload", formData);
  return response.data;
};
