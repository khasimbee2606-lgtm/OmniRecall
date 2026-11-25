import "../assets/styles/imageViewer.css";

function ImageViewer({ image, onClose }) {
  if (!image) return null;

  const isVideo = image.type === "video";

  return (
    <div className="viewer-overlay" onClick={onClose}>
      <div className="viewer-content" onClick={(e) => e.stopPropagation()}>
        {/* ===========================
            Close Button
        =========================== */}

        <button className="close-btn" onClick={onClose}>
          ✕
        </button>

        {/* ===========================
            Viewer
        =========================== */}

        {isVideo ? (
          <video src={image.video} controls autoPlay className="viewer-image" />
        ) : (
          <img
            src={image.image}
            alt={image.filename || ""}
            className="viewer-image"
          />
        )}
      </div>
    </div>
  );
}

export default ImageViewer;
