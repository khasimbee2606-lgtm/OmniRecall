import { useRef } from "react";
import API from "../services/api";

function UploadBox({ onUploadSuccess }) {
  const fileInput = useRef();

  const selectFile = () => {
    fileInput.current.click();
  };

  const uploadFiles = async (event) => {
    const files = Array.from(event.target.files);

    if (files.length === 0) return;

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await API.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      alert(`${files.length} image(s) uploaded successfully!`);

      console.log(response.data);

      if (onUploadSuccess) {
        onUploadSuccess();
      }

      // Allow selecting the same files again
      event.target.value = "";
    } catch (error) {
      console.log(error);

      alert("Upload Failed");
    }
  };

  return (
    <div className="upload-box">
      <h2>📂 Drag & Drop Files</h2>

      <p>or</p>

      <button onClick={selectFile}>Select Images</button>

      <input
        type="file"
        ref={fileInput}
        hidden
        multiple
        accept="image/*"
        onChange={uploadFiles}
      />
    </div>
  );
}

export default UploadBox;
