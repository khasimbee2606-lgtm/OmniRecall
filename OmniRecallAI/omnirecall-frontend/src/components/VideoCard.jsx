import { Trash2, Play } from "lucide-react";

import "../assets/styles/videoCard.css";

function VideoCard({ video, onClick, onDelete }) {
  return (
    <div className="gallery-card" onClick={() => onClick(video)}>
      {/* Thumbnail */}

      <img
        src={video.thumbnail}
        alt={video.filename}
        className="gallery-media"
      />

      {/* Play Icon */}

      <div className="play-icon">
        <Play size={60} fill="white" strokeWidth={1.5} />
      </div>

      {/* Delete */}

      <button
        className="gallery-delete-icon"
        onClick={(e) => {
          e.stopPropagation();

          if (window.confirm(`Delete "${video.filename}" ?`)) {
            onDelete(video);
          }
        }}
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
}

export default VideoCard;
