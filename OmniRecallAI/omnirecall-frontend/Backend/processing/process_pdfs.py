import sys
import json
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


def process_pdfs():

    # =====================================================
    # Initialize Model
    # =====================================================
    pdf_model = PDFModel()

    metadata = []
    embeddings = []

    # =====================================================
    # Create Required Folders
    # =====================================================
    TEXT_FOLDER.mkdir(exist_ok=True)
    THUMBNAILS_FOLDER.mkdir(exist_ok=True)

    # -----------------------------------------
    # Verify Documents Folder Exists
    # -----------------------------------------
    if not DOCUMENTS_FOLDER.exists():
        raise FileNotFoundError(f"Documents folder not found: {DOCUMENTS_FOLDER}")

    # =====================================================
    # Process PDFs
    # =====================================================
    pdf_files = sorted(DOCUMENTS_FOLDER.glob("*.pdf"))

    print(f"\nFound {len(pdf_files)} PDF(s).\n")

    for pdf_path in pdf_files:

        print(f"Processing : {pdf_path.name}")

        # -----------------------------------------
        # Skip PDF On Failure
        # -----------------------------------------
        try:
            result = pdf_model.process_pdf(pdf_path)

            text_file = TEXT_FOLDER / f"{pdf_path.stem}.txt"

            with open(text_file, "w", encoding="utf-8") as file:
                file.write(result["content"])

        except Exception as e:
            print(f"❌ Failed: {pdf_path.name}")
            print(e)
            continue

        print("Embedding:", result["embedding"].shape)

        metadata.append({
            "id": len(metadata) + 1,
            "filename": result["filename"],
            "path": str(pdf_path),
            "text_file": str(text_file),
            "thumbnail": result["thumbnail"],
            "preview": result["preview"],
            "pages": result["pages"],
            "size": round(pdf_path.stat().st_size / (1024 * 1024), 2),
            "document_type": result["document_type"]
        })

        embeddings.append(result["embedding"])

    # =====================================================
    # Save Metadata
    # =====================================================
    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    # =====================================================
    # Save Embeddings
    # =====================================================
    if len(embeddings) > 0:
        np.save(EMBEDDING_FILE, np.array(embeddings, dtype=np.float32))

    else:
        np.save(EMBEDDING_FILE, np.empty((0, 512), dtype=np.float32))

    # =====================================================
    # Completed
    # =====================================================
    print("\n========================================")
    print("PDF Processing Completed")
    print("========================================")
    print(f"PDFs Processed    : {len(metadata)}")
    print(f"Metadata Saved    : {METADATA_FILE}")
    print(f"Embeddings Saved  : {EMBEDDING_FILE}")
    print("========================================")


# =====================================================

if __name__ == "__main__":

    process_pdfs()