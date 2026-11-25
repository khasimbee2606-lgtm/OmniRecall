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

from models.pdf_model import PDFModel

# =====================================================
# Paths
# =====================================================

DOCUMENTS_FOLDER = BACKEND_DIR / "documents"
TEXT_FOLDER = BACKEND_DIR / "text_data"
THUMBNAILS_FOLDER = BACKEND_DIR / "thumbnails"
METADATA_FILE = BACKEND_DIR / "metadata" / "pdf_metadata.json"
EMBEDDING_FILE = BACKEND_DIR / "embeddings" / "pdf_embeddings.npy"


class PDFUploadProcessor:

    def __init__(self):

        self.model = PDFModel()

        DOCUMENTS_FOLDER.mkdir(exist_ok=True)
        TEXT_FOLDER.mkdir(exist_ok=True)
        THUMBNAILS_FOLDER.mkdir(exist_ok=True)
        METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        EMBEDDING_FILE.parent.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # Process Uploaded PDF
    # =====================================================
    def process(self, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"Uploaded PDF not found : {pdf_path}")

        destination = DOCUMENTS_FOLDER / pdf_path.name

        # -----------------------------------------
        # Duplicate Check
        # -----------------------------------------
        if destination.exists():

            if pdf_path.resolve() != destination.resolve():
                try:
                    pdf_path.unlink()
                except Exception:
                    pass

            return {
                "status": "error",
                "message": "PDF already exists."
            }

        # -----------------------------------------
        # Copy PDF
        # -----------------------------------------
        shutil.copy2(pdf_path, destination)

        # -----------------------------------------
        # Process PDF
        # -----------------------------------------
        try:
            result = self.model.process_pdf(destination)

        except Exception as e:
            # Remove copied PDF if processing fails
            if destination.exists():
                destination.unlink()

            raise Exception(f"PDF processing failed : {e}")

        # -----------------------------------------
        # Save Extracted Text
        # -----------------------------------------
        text_file = TEXT_FOLDER / f"{destination.stem}.txt"

        try:
            with open(text_file, "w", encoding="utf-8") as file:
                file.write(result["content"])

        except Exception as e:
            if destination.exists():
                destination.unlink()

            raise Exception(f"Unable to save extracted text : {e}")

        # -----------------------------------------
        # Load Existing Metadata
        # -----------------------------------------
        if METADATA_FILE.exists():
            with open(METADATA_FILE, "r", encoding="utf-8") as file:
                metadata = json.load(file)

        else:
            metadata = []

        # -----------------------------------------------------
        # Assign Id
        # -------------------------------------------------
        # "id": len(metadata) + 1 reuses ids once something has
        # been deleted from the middle of the list — e.g. ids
        # [1, 2, 3], delete id 2, list length drops to 2, and the
        # next upload would get id 2 + 1 = 3, colliding with the
        # PDF that already has id 3. Continue from the highest id
        # actually on file instead, so ids are always unique.
        # =====================================================
        existing_ids = [
            item.get("id")
            for item in metadata
            if isinstance(item.get("id"), int)
        ]

        next_id = (max(existing_ids) + 1) if existing_ids else 1

        metadata.append({
            "id": next_id,
            "filename": result["filename"],
            "path": str(destination),
            "text_file": str(text_file),
            "thumbnail": result["thumbnail"],
            "preview": result["preview"],
            "pages": result["pages"],
            "size": round(destination.stat().st_size / (1024 * 1024), 2),
            "document_type": result["document_type"]
        })

        # -----------------------------------------
        # Save Metadata
        # -----------------------------------------
        try:
            with open(METADATA_FILE, "w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=4)

        except Exception as e:
            # Delete copied PDF and extracted text if metadata saving fails
            if destination.exists():
                destination.unlink()

            if text_file.exists():
                text_file.unlink()

            raise Exception(f"Unable to save metadata : {e}")

        # -----------------------------------------
        # Update Embeddings
        # -----------------------------------------
        embedding = np.asarray(result["embedding"], dtype=np.float32)

        if EMBEDDING_FILE.exists():
            embeddings = np.load(EMBEDDING_FILE)

            if embeddings.size == 0:
                embeddings = np.array([embedding], dtype=np.float32)

            else:
                embeddings = np.vstack((embeddings, embedding))

        else:
            embeddings = np.array([embedding], dtype=np.float32)

        # Save embeddings as float32 to keep the file consistent
        np.save(EMBEDDING_FILE, embeddings.astype(np.float32))

        # -----------------------------------------
        # Remove Temporary Uploaded File
        # -----------------------------------------
        try:
            if pdf_path.exists():
                if pdf_path.resolve() != destination.resolve():
                    pdf_path.unlink()

        except Exception:
            pass

        return {
            "status": "success",
            "message": "PDF uploaded successfully.",
            "id": next_id,
            "filename": result["filename"]
        }