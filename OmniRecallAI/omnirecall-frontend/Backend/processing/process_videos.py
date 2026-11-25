import os
import sys
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm

# =====================================================
# Backend Path
# =====================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from models.video_model import VideoModel

# =====================================================
# Paths
# =====================================================

VIDEOS_FOLDER = BACKEND_DIR / "videos"

VIDEO_FRAMES_FOLDER = BACKEND_DIR / "video_frames"

METADATA_DIR = BACKEND_DIR / "metadata"

EMBEDDINGS_DIR = BACKEND_DIR / "embeddings"

METADATA_FILE = METADATA_DIR / "video_metadata.json"

EMBEDDING_FILE = EMBEDDINGS_DIR / "video_embeddings.npy"

# =====================================================


def process_videos():

    model = VideoModel()

    metadata = []

    embeddings = []

    VIDEO_FRAMES_FOLDER.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------
    # Verify Videos Folder Exists
    # -----------------------------------------
    if not VIDEOS_FOLDER.exists():
        raise FileNotFoundError(f"Videos folder not found: {VIDEOS_FOLDER}")

    extensions = (
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".wmv",
        ".flv",
        ".webm"
    )

    videos = sorted([
        video
        for video in os.listdir(VIDEOS_FOLDER)
        if video.lower().endswith(extensions)
    ])

    print(f"\nFound {len(videos)} videos.\n")

    # -----------------------------------------
    # Track Successes / Failures Separately
    # -----------------------------------------
    # len(videos) is how many videos were FOUND, not how many
    # were actually processed — a video that fails and hits
    # `continue` below never gets appended to metadata or
    # embeddings, so it shouldn't be counted as processed in
    # the final summary either.
    # -----------------------------------------
    processed_count = 0

    failed_videos = []

    for index, video_name in enumerate(tqdm(videos), start=1):

        video_path = VIDEOS_FOLDER / video_name

        print(f"\nProcessing : {video_name}")

        # -----------------------------------------
        # Skip Video On Failure
        # -----------------------------------------
        try:
            result = model.process_video(video_path)

        except Exception as e:
            print(f"❌ Failed: {video_name}")
            print(e)
            failed_videos.append(video_name)
            continue

        embeddings.append(result["embedding"])

        print("Embedding:", result["embedding"].shape)

        metadata.append({
            "id": index,
            "filename": result["filename"],
            "path": str(video_path),
            "thumbnail": result["thumbnail"],
            "duration": result["duration"],
            "size": round(video_path.stat().st_size / (1024 * 1024), 2),
            "objects": result["objects"],
            "caption": result["caption"],
            "tags": result["tags"],
            "searchable": result["searchable"],
            "favorite": False,
            "upload_date": ""
        })

        processed_count += 1

    # =================================================
    # Save Metadata
    # =================================================
    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    # =================================================
    # Save Embeddings
    # =================================================
    np.save(
        EMBEDDING_FILE,
        np.array(embeddings, dtype=np.float32)
    )

    print("\n===================================")
    print("Video Processing Completed")
    print("===================================")
    print(f"Videos Found      : {len(videos)}")
    print(f"Videos Processed  : {processed_count}")
    print(f"Videos Failed     : {len(failed_videos)}")

    if failed_videos:
        print("Failed Videos     :")
        for name in failed_videos:
            print(f"  - {name}")

    print(f"Metadata Saved    : {METADATA_FILE}")
    print(f"Embeddings Saved  : {EMBEDDING_FILE}")


# =====================================================

if __name__ == "__main__":

    process_videos()