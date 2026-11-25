from pathlib import Path

# Backend folder
BASE_DIR = Path(__file__).resolve().parent

# Project root (omnirecall-frontend)
PROJECT_DIR = BASE_DIR.parent

# Frontend images folder
IMAGE_FOLDER = PROJECT_DIR / "frontend" / "src" / "assets" / "images"

# Metadata
METADATA_FILE = BASE_DIR / "metadata" / "metadata.json"

# Embeddings
EMBEDDING_FILE = BASE_DIR / "embeddings" / "image_embeddings.npy"