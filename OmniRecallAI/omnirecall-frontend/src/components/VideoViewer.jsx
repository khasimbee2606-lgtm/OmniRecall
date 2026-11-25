import "../assets/styles/videoViewer.css";

function VideoViewer({ video, onClose }) {
  if (!video) return null;

  return (
    <div className="video-viewer-overlay" onClick={onClose}>
      <div
        className="video-viewer-content"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="video-close-btn" onClick={onClose}>
          ✕
        </button>

        <video className="video-player" src={video.video} controls autoPlay>
          Your browser does not support video.
        </video>
      </div>
    </div>
  );
}

export default VideoViewer;
