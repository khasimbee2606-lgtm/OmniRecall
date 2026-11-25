import sys
import json
import shutil
import numpy as np
from pathlib import Path

# =====================================================
# Backend Path
# =====================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

# =====================================================
# Import Video Model
# =====================================================

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
# Video Upload Processor
# =====================================================


class VideoUploadProcessor:

    def __init__(self):
        print("\n========================================")
        print("Initializing Video Upload Processor...")
        print("========================================")

        self.model = VideoModel()

        VIDEOS_FOLDER.mkdir(parents=True, exist_ok=True)
        VIDEO_FRAMES_FOLDER.mkdir(parents=True, exist_ok=True)
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

        print("✓ Video folders verified")
        print("========================================\n")

    # =====================================================
    # Upload & Process Video
    # =====================================================
    def process(self, uploaded_video):
        uploaded_video = Path(uploaded_video)

        # -----------------------------------------
        # Validate File
        # -----------------------------------------
        if not uploaded_video.exists():
            raise FileNotFoundError(
                f"Uploaded video not found : {uploaded_video}"
            )

        destination = VIDEOS_FOLDER / uploaded_video.name

        # -----------------------------------------
        # Duplicate Check
        # -----------------------------------------
        if destination.exists():

            if uploaded_video.resolve() != destination.resolve():
                try:
                    uploaded_video.unlink()
                except Exception:
                    pass

            return {
                "status": "error",
                "message": "Video already exists."
            }

        # -----------------------------------------
        # Copy Video
        # -----------------------------------------
        shutil.copy2(uploaded_video, destination)

        print(f"✓ Video Copied : {destination.name}")

        # -----------------------------------------
        # Process Video
        # -----------------------------------------
        try:
            result = self.model.process_video(destination)

        except Exception as e:
            # Remove copied video if processing fails
            if destination.exists():
                destination.unlink()

            raise Exception(f"Video processing failed : {e}")

        print("✓ Video Processed Successfully")
        print("Embedding Shape :", result["embedding"].shape)

        # =====================================================
        # Load Existing Metadata
        # =====================================================
        if METADATA_FILE.exists():

            try:
                with open(METADATA_FILE, "r", encoding="utf-8") as file:
                    metadata = json.load(file)

            except Exception:
                metadata = []

        else:
            metadata = []

        # =====================================================
        # Check Existing Video
        # =====================================================
        existing_index = -1

        for index, item in enumerate(metadata):
            if item.get("filename", "").lower() == result["filename"].lower():
                existing_index = index
                break

        # =====================================================
        # Assign Id
        # -----------------------------------------------------
        # process_videos.py (the batch script) assigns integer
        # ids starting at 1. This upload path previously assigned
        # no "id" at all, which crashed /videos in app.py for
        # every request the moment one id-less entry existed.
        #
        # On update, keep the video's existing id. On insert,
        # continue from the highest id currently on file so ids
        # never collide with batch-processed entries.
        # =====================================================
        existing_ids = [
            item.get("id")
            for item in metadata
            if isinstance(item.get("id"), int)
        ]

        next_id = (max(existing_ids) + 1) if existing_ids else 1

        if existing_index != -1:
            video_id = metadata[existing_index].get("id", next_id)
        else:
            video_id = next_id

        # =====================================================
        # Metadata Entry
        # =====================================================
        new_item = {
            "id": video_id,
            "filename": result["filename"],
            "thumbnail": result["thumbnail"],
            "duration": result["duration"],
            # video_model.py already deduplicates objects (via
            # Counter) and orders them by frequency — dedup here
            # is a harmless safety net, but must preserve that
            # order rather than re-sorting alphabetically.
            "objects": list(dict.fromkeys(result["objects"])),
            "caption": result["caption"],
            "tags": sorted(set(result["tags"])),
            "searchable": result["searchable"],
            "favorite": False,
            "upload_date": ""
        }

        # =====================================================
        # Add / Update Metadata
        # =====================================================
        if existing_index == -1:
            metadata.append(new_item)
            print("✓ New Video Metadata Added")

        else:
            metadata[existing_index] = new_item
            print("✓ Existing Video Metadata Updated")

        # =====================================================
        # Save Metadata
        # =====================================================
        try:
            with open(METADATA_FILE, "w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=4)

        except Exception as e:
            # Delete copied video if metadata saving fails
            if destination.exists():
                destination.unlink()

            raise Exception(f"Unable to save metadata : {e}")

        print("✓ Video Metadata Saved")

        # =====================================================
        # Update Embeddings
        # =====================================================
        embedding = np.asarray(result["embedding"], dtype=np.float32)

        # Ensure embedding is 1D
        embedding = embedding.reshape(-1)

        # video_model.py already returns a normalized embedding;
        # this is a harmless safety net in case that ever changes.
        embedding_norm = np.linalg.norm(embedding)

        if embedding_norm > 0:
            embedding = embedding / embedding_norm

        if EMBEDDING_FILE.exists():

            try:
                embeddings = np.load(EMBEDDING_FILE)

            except Exception:
                embeddings = np.empty((0, embedding.shape[0]), dtype=np.float32)

        else:
            embeddings = np.empty((0, embedding.shape[0]), dtype=np.float32)

        # Handle empty embeddings file
        if embeddings.size == 0:
            embeddings = np.empty((0, embedding.shape[0]), dtype=np.float32)

        # Add or Update
        if existing_index == -1:
            embeddings = np.vstack((embeddings, embedding))
            print("✓ New Video Embedding Added")

        else:
            # Safety check in case metadata and embeddings
            # become out of sync.
            if existing_index < len(embeddings):
                embeddings[existing_index] = embedding
                print("✓ Existing Video Embedding Updated")

            else:
                embeddings = np.vstack((embeddings, embedding))
                print("✓ Missing Video Embedding Appended")

        # Save embeddings as float32 to keep the file consistent
        np.save(EMBEDDING_FILE, embeddings.astype(np.float32))

        print("✓ Video Embeddings Saved")

        # =====================================================
        # Remove Temporary Uploaded File
        # =====================================================
        try:
            if uploaded_video.exists():
                if uploaded_video.resolve() != destination.resolve():
                    uploaded_video.unlink()

        except Exception:
            pass

        # =====================================================
        # Success Response
        # =====================================================
        print("\n========================================")
        print("Video Upload Completed Successfully")
        print("========================================")
        print(f"Filename : {result['filename']}")
        print(f"Duration : {result['duration']}")
        print(f"Objects  : {result['objects']}")
        print(f"Caption  : {result['caption']}")
        print("========================================\n")

        return {
            "status": "success",
            "id": video_id,
            "filename": result["filename"],
            "thumbnail": result["thumbnail"],
            "duration": result["duration"],
            "objects": result["objects"],
            "caption": result["caption"],
            "tags": result["tags"],
            "searchable": result["searchable"]
        }


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    processor = VideoUploadProcessor()

    video_path = input("Video Path : ").strip().strip('"')

    response = processor.process(video_path)

    print("\n========================================")
    print(response)
    print("========================================")