import { useEffect, useState } from "react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import GalleryGrid from "../components/GalleryGrid";
import ImageViewer from "../components/ImageViewer";
import VideoViewer from "../components/VideoViewer";

import API from "../services/api";

function Gallery() {
  const [galleryData, setGalleryData] = useState([]);

  const [selectedImage, setSelectedImage] = useState(null);

  const [selectedVideo, setSelectedVideo] = useState(null);

  // ------------------------------------
  // Load Gallery
  // ------------------------------------

  const loadGallery = async () => {
    try {
      const response = await API.get("/gallery");

      setGalleryData(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    loadGallery();
  }, []);

  // ------------------------------------
  // Open Viewer
  // ------------------------------------

  const openMemory = (item) => {
    if (item.type === "video") {
      setSelectedVideo(item);
    } else {
      setSelectedImage(item);
    }
  };

  // ------------------------------------
  // Delete Memory
  // ------------------------------------

  const deleteMemory = async (item) => {
    try {
      if (item.type === "video") {
        await API.delete(`/delete_video/${item.filename}`);
      } else {
        await API.delete(`/delete/${item.filename}`);
      }

      setSelectedImage(null);
      setSelectedVideo(null);

      loadGallery();
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
      }}
    >
      <Sidebar />

      <div
        style={{
          marginLeft: "240px",
          padding: "25px",
        }}
      >
        <Navbar />

        <h1
          style={{
            color: "white",
            fontSize: "38px",
            marginBottom: "30px",
            fontWeight: "bold",
          }}
        >
          Gallery
        </h1>

        <GalleryGrid
          images={galleryData}
          onImageClick={openMemory}
          onDelete={deleteMemory}
        />
      </div>

      {/* Image Viewer */}

      <ImageViewer
        image={selectedImage}
        onClose={() => setSelectedImage(null)}
      />

      {/* Video Viewer */}

      <VideoViewer
        video={selectedVideo}
        onClose={() => setSelectedVideo(null)}
      />
    </div>
  );
}

export default Gallery;
