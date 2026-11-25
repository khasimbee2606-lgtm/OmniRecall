import GalleryCard from "./GalleryCard";

import "../assets/styles/galleryGrid.css";

import API from "../services/api";

function GalleryGrid({ images, onImageClick, onRefresh }) {
  // =====================================
  // Delete Memory
  // =====================================

  const deleteMemory = async (item) => {
    try {
      if (item.type === "video") {
        await API.delete(`/delete_video/${item.filename}`);
      } else {
        await API.delete(`/delete/${item.filename}`);
      }

      if (onRefresh) {
        onRefresh();
      }
    } catch (err) {
      console.log(err);
    }
  };

  // =====================================
  // UI
  // =====================================

  return (
    <div className="gallery-grid">
      {images && images.length > 0 ? (
        images.map((item) => (
          <GalleryCard
            key={item.id || `${item.type}-${item.filename}`}
            image={item}
            onClick={onImageClick}
            onDelete={deleteMemory}
          />
        ))
      ) : (
        <div className="no-images">
          <h2>No Memories Found</h2>
        </div>
      )}
    </div>
  );
}

export default GalleryGrid;
