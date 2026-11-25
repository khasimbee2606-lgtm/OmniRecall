import { Trash2, Play } from "lucide-react";
import "../assets/styles/galleryCard.css";

function GalleryCard({ image, onClick, onDelete }) {
  const isVideo = image.type === "video";

  return (
    <div className="gallery-card" onClick={() => onClick && onClick(image)}>
      <div className="gallery-thumbnail">
        {isVideo ? (
          <>
            <img
              src={image.thumbnail}
              alt={image.filename}
              className="gallery-media"
            />

            <div className="play-icon">
              <Play size={60} fill="white" strokeWidth={1.5} />
            </div>
          </>
        ) : (
          <img
            src={image.image}
            alt={image.filename}
            className="gallery-media"
          />
        )}
      </div>

      <button
        className="gallery-delete-icon"
        onClick={(e) => {
          e.stopPropagation();
          onDelete(image);
        }}
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
}

export default GalleryCard;
