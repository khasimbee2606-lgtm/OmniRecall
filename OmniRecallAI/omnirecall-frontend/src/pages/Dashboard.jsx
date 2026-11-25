import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import GalleryGrid from "../components/GalleryGrid";
import ImageViewer from "../components/ImageViewer";

import API from "../services/api";

import "../assets/styles/dashboard.css";

function Dashboard() {
  const [galleryData, setGalleryData] = useState([]);

  const [videoData, setVideoData] = useState([]);

  const [pdfData, setPdfData] = useState([]);

  const [selectedMemory, setSelectedMemory] = useState(null);

  // ==========================
  // Load Data
  // ==========================

  useEffect(() => {
    loadGallery();
    loadVideos();
    loadDocuments();
  }, []);

  // ==========================
  // Load Images
  // ==========================

  const loadGallery = async () => {
    try {
      const response = await API.get("/gallery");

      setGalleryData(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  // ==========================
  // Load Videos
  // ==========================

  const loadVideos = async () => {
    try {
      const response = await API.get("/videos");

      setVideoData(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  // ==========================
  // Load Documents
  // ==========================

  const loadDocuments = async () => {
    try {
      const response = await API.get("/documents");

      setPdfData(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  // ==========================
  // Dashboard Counts
  // ==========================
  // /gallery returns images AND videos combined (each item
  // tagged with "type"), since the Gallery page shows both
  // together. For the dashboard's image-only stats and the
  // "Recent Images" grid below, that combined list needs to
  // be filtered down to images only — otherwise videos get
  // counted as images, and video items (which don't have an
  // "image" field) get passed into a grid that expects one.

  const imagesOnly = galleryData.filter((item) => item.type === "image");

  const totalImages = imagesOnly.length;

  const totalVideos = videoData.length;

  const totalPDFs = pdfData.length;

  return (
    <>
      <Sidebar />

      <div className="dashboard-page">
        <Navbar />

        <div className="dashboard-container">
          <h1 className="dashboard-heading">Dashboard</h1>

          {/* Statistics */}

          <div className="dashboard-grid">
            <div className="dashboard-card">
              <h2>{totalImages}</h2>
              <p>Total Images</p>
            </div>

            <div className="dashboard-card">
              <h2>{totalVideos}</h2>
              <p>Total Videos</p>
            </div>

            <div className="dashboard-card">
              <h2>{totalPDFs}</h2>
              <p>Total PDFs</p>
            </div>
          </div>

          {/* Images */}

          <div className="dashboard-section">
            <h2 className="dashboard-subheading">Recent Images</h2>

            <GalleryGrid
              images={imagesOnly}
              onImageClick={setSelectedMemory}
              onRefresh={loadGallery}
            />
          </div>
        </div>
      </div>

      <ImageViewer
        image={selectedMemory}
        onClose={() => setSelectedMemory(null)}
      />
    </>
  );
}

export default Dashboard;
