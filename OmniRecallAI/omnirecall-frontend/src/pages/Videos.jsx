import { useEffect, useState } from "react";

import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import SearchBar from "../components/SearchBar";
import VoiceSearch from "../components/VoiceSearch";
import VideoGrid from "../components/VideoGrid";
import VideoViewer from "../components/VideoViewer";

import API from "../services/api";

import "../assets/styles/documents.css";
import "../assets/styles/videoGrid.css";
import "../assets/styles/videoCard.css";
import "../assets/styles/videoViewer.css";

function Videos() {
  const [videos, setVideos] = useState([]);
  const [viewer, setViewer] = useState(null);
  const [query, setQuery] = useState("");

  // ==========================
  // Load Videos
  // ==========================

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      const res = await API.get("/videos");
      setVideos(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  // ==========================
  // Search Videos
  // ==========================

  const searchVideos = async (text) => {
    setQuery(text);

    if (text.trim() === "") {
      loadVideos();
      return;
    }

    try {
      const res = await API.post("/video_search", {
        query: text,
      });

      setVideos(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <>
      <Sidebar />

      <div className="documents-page">
        <Navbar />

        <div className="documents-container">
          {/* Header */}

          <div className="documents-header">
            <h1 className="documents-title">🎥 Videos</h1>

            <p className="documents-subtitle">
              Search your uploaded videos instantly.
            </p>
          </div>

          {/* Search */}

          <div className="documents-search">
            <SearchBar
              value={query}
              placeholder="Search videos..."
              onChange={(e) => searchVideos(e.target.value)}
            />

            <VoiceSearch onResult={(text) => searchVideos(text)} />
          </div>

          {/* Count */}

          <div className="document-count">Total Videos : {videos.length}</div>

          {/* Grid */}

          <VideoGrid
            videos={videos}
            onVideoClick={setViewer}
            onRefresh={loadVideos}
          />
        </div>

        <VideoViewer video={viewer} onClose={() => setViewer(null)} />
      </div>
    </>
  );
}

export default Videos;
