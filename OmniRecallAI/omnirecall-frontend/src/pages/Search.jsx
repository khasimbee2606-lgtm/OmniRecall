import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import SearchBar from "../components/SearchBar";
import VoiceSearch from "../components/VoiceSearch";
import GalleryGrid from "../components/GalleryGrid";
import ImageViewer from "../components/ImageViewer";

import API from "../services/api";

import "../assets/styles/search.css";

function Search() {
  const [images, setImages] = useState([]);

  const [viewer, setViewer] = useState(null);

  const [query, setQuery] = useState("");

  // ============================================
  // Load Complete Gallery (Images Only)
  // ============================================
  // /gallery returns images AND videos combined (each item
  // tagged with "type"), since Gallery page shows both
  // together. This page should show images only, so the
  // combined list is filtered down before being displayed.

  useEffect(() => {
    loadGallery();
  }, []);

  const loadGallery = async () => {
    try {
      const res = await API.get("/gallery");

      const imagesOnly = res.data.filter((item) => item.type === "image");

      setImages(imagesOnly);
    } catch (err) {
      console.log(err);
    }
  };

  // ============================================
  // Search Images Only
  // ============================================

  const searchImages = async (text) => {
    setQuery(text);

    // Empty Search -> Gallery

    if (text.trim() === "") {
      loadGallery();

      return;
    }

    try {
      const res = await API.post("/image_search", {
        query: text,
      });

      setImages(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <>
      <Sidebar />

      <div className="search-page">
        <Navbar />

        <div className="search-container">
          {/* Header */}

          <div className="search-header">
            <h1 className="search-title">🔍 AI Memory Search</h1>

            <p className="search-subtitle">
              Search your memories using text or voice.
            </p>
          </div>

          {/* Search Controls */}

          <div className="search-controls">
            <SearchBar
              value={query}
              placeholder="Search people, objects, places..."
              onChange={(e) => searchImages(e.target.value)}
            />

            <VoiceSearch onResult={(text) => searchImages(text)} />
          </div>

          {/* Results */}

          <div className="search-results">
            <GalleryGrid images={images} onImageClick={setViewer} />
          </div>
        </div>

        {/* Image Viewer */}

        <ImageViewer image={viewer} onClose={() => setViewer(null)} />
      </div>
    </>
  );
}

export default Search;
