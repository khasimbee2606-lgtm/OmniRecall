import VideoCard from "./VideoCard";

import "../assets/styles/galleryGrid.css";

import API from "../services/api";

function VideoGrid({ videos, onVideoClick, onRefresh }) {
  const deleteVideo = async (video) => {
    try {
      await API.delete(`/delete_video/${video.filename}`);

      if (onRefresh) {
        onRefresh();
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="gallery-grid">
      {videos.length > 0 ? (
        videos.map((video) => (
          <VideoCard
            key={video.filename}
            video={video}
            onClick={onVideoClick}
            onDelete={deleteVideo}
          />
        ))
      ) : (
        <div className="no-images">
          <h2>No Videos Found</h2>
        </div>
      )}
    </div>
  );
}

export default VideoGrid;
