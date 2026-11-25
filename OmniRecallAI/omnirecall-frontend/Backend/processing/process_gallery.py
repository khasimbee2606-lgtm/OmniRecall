import os
import sys
import json
import numpy as np
from pathlib import Path
from tqdm import tqdm

# --------------------------------------------------------
# Add Backend folder to Python path
# --------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from models.registry import get_clip_model, get_detector, get_blip_model
from utils.tag_generator import generate_tags

# --------------------------------------------------------
# Paths
# --------------------------------------------------------

PROJECT_DIR = BACKEND_DIR.parent

IMAGE_FOLDER = PROJECT_DIR / "src" / "assets" / "images"

METADATA_DIR = BACKEND_DIR / "metadata"

EMBEDDINGS_DIR = BACKEND_DIR / "embeddings"

METADATA_FILE = METADATA_DIR / "metadata.json"

EMBEDDING_FILE = EMBEDDINGS_DIR / "image_embeddings.npy"


# =========================================================

def process_gallery():

    detector = get_detector()

    clip = get_clip_model()

    blip = get_blip_model()

    metadata = []

    embeddings = []

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------
    # Verify Image Folder Exists
    # -----------------------------------------
    if not IMAGE_FOLDER.exists():
        raise FileNotFoundError(f"Image folder not found: {IMAGE_FOLDER}")

    extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

    images = sorted([
        image
        for image in os.listdir(IMAGE_FOLDER)
        if image.lower().endswith(extensions)
    ])

    print(f"\nFound {len(images)} images.\n")

    for image_name in tqdm(images):

        image_path = IMAGE_FOLDER / image_name

        # -----------------------------------------
        # Skip Image On Failure
        # -----------------------------------------
        try:
            # --------------------------------------------
            # Object Detection
            # --------------------------------------------
            detection = detector.detect_objects(str(image_path))

            # --------------------------------------------
            # Caption
            # --------------------------------------------
            caption = blip.generate_caption(str(image_path))

            print("Caption :", caption)

            # --------------------------------------------
            # Smart Tags
            # --------------------------------------------
            tags = generate_tags(image_name, detection["objects"])

            # --------------------------------------------
            # Searchable Text
            # --------------------------------------------
            searchable = " ".join(
                [image_name.lower()]
                + [obj.lower() for obj in detection["objects"]]
                + [tag.lower() for tag in tags]
                + [caption.lower()]
            )

            # --------------------------------------------
            # CLIP Embedding
            # --------------------------------------------
            embedding = clip.encode_image(str(image_path))

        except Exception as e:
            print(f"❌ Failed: {image_name}")
            print(e)
            continue

        embeddings.append(embedding)

        print("Embedding:", embedding.shape)

        # --------------------------------------------
        # Metadata
        # --------------------------------------------
        metadata.append({
            "filename": image_name,
            "objects": detection["objects"],
            "confidence": detection["confidence"],
            "caption": caption,
            "tags": tags,
            "searchable": searchable,
            "favorite": False,
            "upload_date": ""
        })

    # ===================================================
    # Save Metadata
    # ===================================================
    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    # ===================================================
    # Save Embeddings
    # ===================================================
    np.save(
        EMBEDDING_FILE,
        np.array(embeddings, dtype=np.float32)
    )

    print("\n===================================")
    print("Gallery Processing Completed")
    print("===================================")
    print(f"Images Processed : {len(images)}")
    print(f"Metadata Saved   : {METADATA_FILE}")
    print(f"Embeddings Saved : {EMBEDDING_FILE}")


# =========================================================

if __name__ == "__main__":

    process_gallery()