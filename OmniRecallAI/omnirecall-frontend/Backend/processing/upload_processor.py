import sys
import json
import shutil
import numpy as np
from pathlib import Path

# ==========================================================
# Backend Path
# ==========================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

# ==========================================================

from models.registry import get_clip_model, get_detector, get_blip_model
from utils.tag_generator import generate_tags

# ==========================================================
# Paths
# ==========================================================

PROJECT_DIR = BACKEND_DIR.parent

IMAGE_FOLDER = PROJECT_DIR / "src" / "assets" / "images"

METADATA_FILE = BACKEND_DIR / "metadata" / "metadata.json"

EMBEDDING_FILE = BACKEND_DIR / "embeddings" / "image_embeddings.npy"

# ==========================================================


class UploadProcessor:

    def __init__(self):

        # -----------------------------------------
        # AI Models (Shared Across The App)
        # -----------------------------------------
        self.detector = get_detector()
        self.clip = get_clip_model()
        self.blip = get_blip_model()

        IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)
        METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        EMBEDDING_FILE.parent.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # Process Uploaded Image
    # =====================================================
    def process(self, uploaded_file_path):

        uploaded_file_path = Path(uploaded_file_path)

        if not uploaded_file_path.exists():
            raise FileNotFoundError(
                f"Uploaded image not found : {uploaded_file_path}"
            )

        filename = uploaded_file_path.name

        destination = IMAGE_FOLDER / filename

        # ==================================================
        # Copy Image
        # ==================================================
        shutil.copy(uploaded_file_path, destination)

        print("✓ Image Copied")

        try:
            # ==================================================
            # Object Detection
            # ==================================================
            detection = self.detector.detect_objects(str(destination))

            objects = detection.get("objects", [])

            confidence = detection.get("confidence", [])

            print("✓ Objects :", objects)

            # ==================================================
            # BLIP Caption
            # ==================================================
            caption = self.blip.generate_caption(str(destination))

            print("✓ Caption :", caption)

            # ==================================================
            # Generate Smart Tags
            # ==================================================
            tags = generate_tags(filename, objects)

            print("✓ Tags :", tags)

            # ==================================================
            # Searchable Text
            # ==================================================
            searchable = " ".join(
                [filename.lower()]
                + [obj.lower() for obj in objects]
                + [tag.lower() for tag in tags]
                + [caption.lower()]
            )

            print("✓ Searchable :", searchable)

            # ==================================================
            # CLIP Embedding
            # ==================================================
            embedding = np.asarray(
                self.clip.encode_image(str(destination)),
                dtype=np.float32
            )

        except Exception as e:
            # Remove copied image if processing fails
            if destination.exists():
                destination.unlink()

            raise Exception(f"Image processing failed : {e}")

        # ==================================================
        # Load Existing Metadata
        # ==================================================
        if METADATA_FILE.exists():
            try:
                with open(METADATA_FILE, "r", encoding="utf-8") as file:
                    metadata = json.load(file)

            except (json.JSONDecodeError, OSError):
                metadata = []

        else:
            metadata = []

        # ==================================================
        # Check Duplicate
        # ==================================================
        existing_index = -1

        for i, item in enumerate(metadata):
            if item["filename"].lower() == filename.lower():
                existing_index = i
                break

        # ==================================================
        # Metadata Entry
        # ==================================================
        new_item = {
            "filename": filename,
            "objects": objects,
            "confidence": confidence,
            "caption": caption,
            "tags": tags,
            "searchable": searchable,
            "favorite": False,
            "upload_date": ""
        }

        # ==================================================
        # Add / Update Metadata
        # ==================================================
        if existing_index == -1:
            metadata.append(new_item)
            print("✓ New Metadata Added")

        else:
            metadata[existing_index] = new_item
            print("✓ Existing Metadata Updated")

        try:
            with open(METADATA_FILE, "w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=4)

        except OSError as e:
            # Delete copied image if metadata saving fails
            if destination.exists():
                destination.unlink()

            raise Exception(f"Unable to save metadata : {e}")

        print("✓ Metadata Saved")

        # ==================================================
        # Update Embeddings
        # ==================================================
        try:
            embeddings = np.load(EMBEDDING_FILE)

        except (FileNotFoundError, OSError, ValueError):
            embeddings = np.empty((0, embedding.shape[0]), dtype=np.float32)

        if existing_index == -1:
            embeddings = np.vstack((embeddings, embedding))
            print("✓ New Embedding Added")

        else:
            # Safety check in case metadata and embeddings
            # become out of sync.
            if existing_index < len(embeddings):
                embeddings[existing_index] = embedding
                print("✓ Existing Embedding Updated")

            else:
                embeddings = np.vstack((embeddings, embedding))
                print("✓ Missing Embedding Appended")

        # Save embeddings as float32 to keep the file consistent
        np.save(EMBEDDING_FILE, embeddings.astype(np.float32))

        print("✓ Embeddings Saved")

        # ==================================================

        return {
            "status": "success",
            "filename": filename,
            "objects": objects,
            "confidence": confidence,
            "caption": caption,
            "tags": tags,
            "searchable": searchable
        }


# ==========================================================

if __name__ == "__main__":

    processor = UploadProcessor()

    image_path = input("Image Path : ").strip().strip('"')

    result = processor.process(image_path)

    print("\n====================================")
    print(result)
    print("====================================")