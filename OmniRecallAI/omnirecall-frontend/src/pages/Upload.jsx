import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import API from "../services/api";
import "../assets/styles/upload.css";

function Upload() {
  const [imageFiles, setImageFiles] = useState([]);
  const [pdfFiles, setPdfFiles] = useState([]);
  const [videoFiles, setVideoFiles] = useState([]);

  // ==============================
  // Poll Video Processing Status
  // ==============================
  // A video upload returns immediately with "processing" —
  // the actual success/failure only becomes known once the
  // background job finishes. This polls the status endpoint
  // until every accepted video is done (success or error).

  const pollVideoStatus = (filename) => {
    return new Promise((resolve) => {
      const check = async () => {
        try {
          const res = await API.get(`/video_upload_status/${filename}`);

          if (res.data.status === "processing") {
            setTimeout(check, 2000);
          } else {
            resolve({ filename, ...res.data });
          }
        } catch (err) {
          resolve({
            filename,
            status: "error",
            message: "Unable to check processing status",
          });
        }
      };

      check();
    });
  };

  // ==============================
  // Upload Images
  // ==============================

  const uploadImage = async () => {
    if (imageFiles.length === 0) {
      alert("Select Images");
      return;
    }

    const formData = new FormData();

    imageFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const res = await API.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const results = res.data.results || [];

      const succeeded = results.filter((r) => r.status === "success");
      const failed = results.filter((r) => r.status !== "success");

      if (failed.length === 0) {
        alert(`${succeeded.length} image(s) uploaded successfully.`);
      } else {
        alert(
          `${succeeded.length} image(s) uploaded, ${failed.length} failed:\n` +
            failed.map((f) => `${f.filename}: ${f.message}`).join("\n"),
        );
      }

      setImageFiles([]);
    } catch (error) {
      console.log(error);

      const results = error?.response?.data?.results || [];

      if (results.length > 0) {
        alert(
          "Upload failed:\n" +
            results.map((f) => `${f.filename}: ${f.message}`).join("\n"),
        );
      } else {
        alert("Upload Failed");
      }
    }
  };

  // ==============================
  // Upload PDFs
  // ==============================

  const uploadPDF = async () => {
    if (pdfFiles.length === 0) {
      alert("Select PDFs");
      return;
    }

    const formData = new FormData();

    pdfFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const res = await API.post("/pdf_upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const results = res.data.results || [];

      const succeeded = results.filter((r) => r.status === "success");
      const failed = results.filter((r) => r.status !== "success");

      if (failed.length === 0) {
        alert(`${succeeded.length} PDF(s) uploaded successfully.`);
      } else {
        alert(
          `${succeeded.length} PDF(s) uploaded, ${failed.length} failed:\n` +
            failed.map((f) => `${f.filename}: ${f.message}`).join("\n"),
        );
      }

      setPdfFiles([]);
    } catch (error) {
      console.log(error);

      const results = error?.response?.data?.results || [];

      if (results.length > 0) {
        alert(
          "Upload failed:\n" +
            results.map((f) => `${f.filename}: ${f.message}`).join("\n"),
        );
      } else {
        alert("Upload Failed");
      }
    }
  };

  // ==============================
  // Upload Videos
  // ==============================

  const uploadVideo = async () => {
    if (videoFiles.length === 0) {
      alert("Select Videos");
      return;
    }

    const formData = new FormData();

    videoFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const res = await API.post("/video_upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const accepted = res.data.accepted || [];
      const rejected = res.data.rejected || [];

      if (accepted.length === 0) {
        alert(
          "No videos were accepted:\n" +
            rejected.map((r) => `${r.filename}: ${r.message}`).join("\n"),
        );
        return;
      }

      alert(
        `${accepted.length} video(s) uploaded, processing in background. ` +
          "You'll see them on the Videos page once ready.",
      );

      setVideoFiles([]);

      // -----------------------------------------
      // Poll each accepted video until it finishes
      // processing, then report any that failed.
      // -----------------------------------------
      const outcomes = await Promise.all(accepted.map(pollVideoStatus));

      const failed = outcomes.filter((o) => o.status !== "success");

      if (failed.length > 0) {
        alert(
          `${failed.length} video(s) failed to process:\n` +
            failed.map((f) => `${f.filename}: ${f.message}`).join("\n"),
        );
      }
    } catch (error) {
      console.log(error);

      const rejected = error?.response?.data?.rejected || [];

      if (rejected.length > 0) {
        alert(
          "Upload failed:\n" +
            rejected.map((r) => `${r.filename}: ${r.message}`).join("\n"),
        );
      } else {
        alert("Upload Failed");
      }
    }
  };

  return (
    <>
      <Sidebar />

      <div className="upload-page">
        <Navbar />

        <div className="upload-container">
          <h1>Upload Memories</h1>

          <p>Upload Images, Videos and PDF Documents to OmniRecall AI.</p>

          <div className="upload-grid">
            {/* Image Upload */}

            <div className="upload-box">
              <div className="upload-icon">🖼</div>

              <h2>Upload Images</h2>

              <p>Select Image Files</p>

              <label className="upload-button">
                Select Images
                <input
                  type="file"
                  hidden
                  multiple
                  accept="image/*"
                  onChange={(e) => setImageFiles(Array.from(e.target.files))}
                />
              </label>

              {imageFiles.length > 0 && (
                <p className="selected-file">
                  {imageFiles.length} image(s) selected
                </p>
              )}

              <button className="upload-submit" onClick={uploadImage}>
                Upload Images
              </button>
            </div>

            {/* PDF Upload */}

            <div className="upload-box">
              <div className="upload-icon">📄</div>

              <h2>Upload Documents</h2>

              <p>Select PDF Files</p>

              <label className="upload-button">
                Select PDF
                <input
                  type="file"
                  hidden
                  multiple
                  accept=".pdf"
                  onChange={(e) => setPdfFiles(Array.from(e.target.files))}
                />
              </label>

              {pdfFiles.length > 0 && (
                <p className="selected-file">
                  {pdfFiles.length} PDF(s) selected
                </p>
              )}

              <button className="upload-submit" onClick={uploadPDF}>
                Upload PDFs
              </button>
            </div>

            {/* Video Upload */}

            <div className="upload-box">
              <div className="upload-icon">🎥</div>

              <h2>Upload Videos</h2>

              <p>Select Video Files</p>

              <label className="upload-button">
                Select Video
                <input
                  type="file"
                  hidden
                  multiple
                  accept="video/*"
                  onChange={(e) => setVideoFiles(Array.from(e.target.files))}
                />
              </label>

              {videoFiles.length > 0 && (
                <p className="selected-file">
                  {videoFiles.length} video(s) selected
                </p>
              )}

              <button className="upload-submit" onClick={uploadVideo}>
                Upload Videos
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Upload;
