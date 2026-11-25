from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from pathlib import Path

import json
import os
import threading
import numpy as np

# =====================================================
# Search Engines
# =====================================================

from search.search_engine import SearchEngine
from search.pdf_search import PDFSearchEngine
from search.video_search import VideoSearchEngine

# =====================================================
# Upload Processors
# =====================================================

from processing.upload_processor import UploadProcessor
from processing.pdf_upload_processor import PDFUploadProcessor
from processing.video_upload_processor import VideoUploadProcessor

# =====================================================
# Flask App
# =====================================================

app = Flask(__name__)

CORS(app)

# =====================================================
# Paths
# =====================================================

BACKEND_DIR = Path(__file__).resolve().parent

PROJECT_DIR = BACKEND_DIR.parent

IMAGE_FOLDER = PROJECT_DIR / "src" / "assets" / "images"

VIDEOS_FOLDER = BACKEND_DIR / "videos"

VIDEO_THUMBNAILS_FOLDER = BACKEND_DIR / "video_frames"

DOCUMENTS_FOLDER = BACKEND_DIR / "documents"

THUMBNAILS_FOLDER = BACKEND_DIR / "thumbnails"

UPLOAD_FOLDER = BACKEND_DIR / "uploads"

# =====================================================
# Metadata Files
# =====================================================

METADATA_FILE = BACKEND_DIR / "metadata" / "metadata.json"

PDF_METADATA_FILE = BACKEND_DIR / "metadata" / "pdf_metadata.json"

VIDEO_METADATA_FILE = BACKEND_DIR / "metadata" / "video_metadata.json"

# =====================================================
# Allowed File Extensions
# =====================================================

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

PDF_EXTENSIONS = {".pdf"}

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}

# =====================================================
# Load AI Models
# =====================================================

engine = SearchEngine()

pdf_engine = PDFSearchEngine()

video_engine = VideoSearchEngine()

# =====================================================
# Upload Processors
# =====================================================

upload_processor = UploadProcessor()

pdf_upload_processor = PDFUploadProcessor()

video_upload_processor = VideoUploadProcessor()

# =====================================================
# Ensure Upload Folder Exists (Once, At Startup)
# =====================================================

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# =====================================================
# Background Video Processing Status
# =====================================================
# Tracks in-progress/completed video uploads so the frontend
# can poll instead of blocking on the upload request itself.

VIDEO_UPLOAD_STATUS = {}
VIDEO_UPLOAD_STATUS_LOCK = threading.Lock()


# =====================================================
# Helpers
# =====================================================

def allowed_file(filename, allowed_extensions):
    """Check the uploaded file's extension against a whitelist."""
    return Path(filename).suffix.lower() in allowed_extensions


def load_json_safe(path, default=None):
    """Load a JSON file, returning `default` if missing or corrupted."""
    if default is None:
        default = []

    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️ Failed to read {path.name} : {e}")
        return default


def save_json_safe(path, data):
    """Save JSON data, raising a clear exception on failure."""
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    except OSError as e:
        raise Exception(f"Unable to save {path.name} : {e}")


def load_embeddings_safe(path):
    """Load an embeddings .npy file, returning None if missing or corrupted."""
    if not path.exists():
        return None

    try:
        return np.load(path, allow_pickle=False)

    except Exception as e:
        print(f"⚠️ Failed to load embeddings {path.name} : {e}")
        return None


# =====================================================
# Home Route
# =====================================================

@app.route("/")
def home():
    return jsonify({
        "message": "OmniRecall AI Backend Running Successfully"
    })


# =====================================================
# Gallery API
# Images + Videos
# =====================================================

@app.route("/gallery", methods=["GET"])
def gallery():

    base_url = request.host_url.rstrip("/")

    gallery = []

    # -------------------------------------------------
    # Images
    # -------------------------------------------------
    image_metadata = load_json_safe(METADATA_FILE, default=[])

    for index, item in enumerate(image_metadata):

        # Defensive: skip a malformed entry instead of letting
        # it take down the whole /gallery response.
        if "filename" not in item:
            print(f"⚠️ Skipping image metadata entry {index} : missing 'filename'")
            continue

        gallery.append({
            "id": f"img_{index + 1}",
            "type": "image",
            "filename": item["filename"],
            "title": item["filename"],
            "image": f"{base_url}/images/{item['filename']}",
            "category": "Gallery",
            "location": item.get("location", "Unknown"),
            "people": ", ".join(item.get("objects", [])),
            "objects": item.get("objects", []),
            "tags": item.get("tags", []),
            "caption": item.get("caption", "")
        })

    # -------------------------------------------------
    # Videos
    # -------------------------------------------------
    video_metadata = load_json_safe(VIDEO_METADATA_FILE, default=[])

    for index, item in enumerate(video_metadata):

        # Defensive: a video entry with no filename/thumbnail
        # can't be rendered usefully — skip it, don't 500.
        if "filename" not in item or "thumbnail" not in item:
            print(f"⚠️ Skipping video metadata entry {index} : missing 'filename' or 'thumbnail'")
            continue

        thumbnail = Path(item["thumbnail"]).name

        # Fall back to a stable, unique id (index-based) instead
        # of crashing when an entry has no "id" (e.g. videos
        # added through /video_upload before this fix).
        video_id = item.get("id", index)

        gallery.append({
            "id": f"vid_{video_id}",
            "type": "video",
            "filename": item["filename"],
            "title": item["filename"],
            "thumbnail": f"{base_url}/video_frames/{thumbnail}",
            "video": f"{base_url}/videos/{item['filename']}",
            "duration": item.get("duration", ""),
            "size": item.get("size", 0),
            "objects": item.get("objects", []),
            "caption": item.get("caption", ""),
            "tags": item.get("tags", [])
        })

    return jsonify(gallery)


# =====================================================
# Image Search API
# =====================================================

@app.route("/search", methods=["POST"])
def search():

    data = request.get_json(silent=True) or {}

    query = data.get("query", "").strip()

    if query == "":
        return jsonify([])

    base_url = request.host_url.rstrip("/")

    # Reload latest metadata every search
    engine.reload_data()
    video_engine.reload_data()

    image_results = engine.search(query)

    video_results = video_engine.search(query)

    results = []

    # -------------------------------------------------
    # Images
    # -------------------------------------------------
    for item in image_results:

        results.append({
            "id": f"img_{item['filename']}",
            "type": "image",
            "filename": item["filename"],
            "image": f"{base_url}/images/{item['filename']}",
            "objects": item.get("objects", []),
            "score": item.get("score", 0)
        })

    # -------------------------------------------------
    # Videos
    # -------------------------------------------------
    for item in video_results:

        results.append({
            "id": f"vid_{item['filename']}",
            "type": "video",
            "filename": item["filename"],
            "thumbnail": f"{base_url}/video_frames/{item['thumbnail']}",
            "video": f"{base_url}/videos/{item['filename']}",
            "duration": item.get("duration", ""),
            "objects": item.get("objects", []),
            "caption": item.get("caption", ""),
            "tags": item.get("tags", []),
            "score": item.get("score", 0)
        })

    # -------------------------------------------------
    # Highest Score First
    # -------------------------------------------------
    results.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(results)


# =====================================================
# Image-Only Search API
# -----------------------------------------------------
# Dedicated endpoint for the Search page, which should
# show images only. /search remains unchanged (still
# returns images + videos combined) in case Gallery or
# any other consumer still relies on that behavior.
# =====================================================

@app.route("/image_search", methods=["POST"])
def image_search():

    data = request.get_json(silent=True) or {}

    query = data.get("query", "").strip()

    if query == "":
        return jsonify([])

    base_url = request.host_url.rstrip("/")

    engine.reload_data()

    raw_results = engine.search(query)

    results = []

    for item in raw_results:

        results.append({
            "filename": item["filename"],
            "image": f"{base_url}/images/{item['filename']}",
            "objects": item.get("objects", []),
            "score": item.get("score", 0)
        })

    return jsonify(results)


# =====================================================
# Image Upload API
# =====================================================

@app.route("/upload", methods=["POST"])
def upload():

    files = request.files.getlist("files")

    if not files:
        return jsonify({
            "status": "error",
            "message": "No files selected"
        }), 400

    results = []

    for file in files:

        if file.filename == "":
            results.append({
                "filename": "",
                "status": "error",
                "message": "Empty filename"
            })
            continue

        if not allowed_file(file.filename, IMAGE_EXTENSIONS):
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": "Unsupported file type for image upload"
            })
            continue

        upload_path = UPLOAD_FOLDER / file.filename

        file.save(upload_path)

        try:
            result = upload_processor.process(upload_path)
            results.append(result)

        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"Image processing failed : {e}"
            })

    # Reload image search engine once after the whole batch
    engine.reload_data()

    overall_status = (
        "success"
        if any(item.get("status") == "success" for item in results)
        else "error"
    )

    status_code = 200 if overall_status == "success" else 400

    return jsonify({
        "status": overall_status,
        "results": results
    }), status_code


# =====================================================
# Documents API
# =====================================================

@app.route("/documents", methods=["GET"])
def documents():

    base_url = request.host_url.rstrip("/")

    metadata = load_json_safe(PDF_METADATA_FILE, default=[])

    documents = []

    for index, item in enumerate(metadata):

        # Defensive: skip malformed entries instead of 500ing
        # the whole /documents response.
        if "id" not in item or "filename" not in item or "thumbnail" not in item:
            print(f"⚠️ Skipping document metadata entry {index} : missing required field")
            continue

        thumbnail_name = Path(item["thumbnail"]).name

        documents.append({
            "id": item["id"],
            "filename": item["filename"],
            "pages": item.get("pages", 0),
            "size": item.get("size", 0),
            "preview": item.get("preview", ""),
            "document_type": item.get("document_type", "PDF"),
            "thumbnail": f"{base_url}/thumbnails/{thumbnail_name}",
            "file": f"{base_url}/pdfs/{item['filename']}"
        })

    return jsonify(documents)


# =====================================================
# PDF Search API
# =====================================================

@app.route("/pdf_search", methods=["POST"])
def pdf_search():

    data = request.get_json(silent=True) or {}

    query = data.get("query", "").strip()

    if query == "":
        return jsonify([])

    base_url = request.host_url.rstrip("/")

    pdf_engine.reload_data()

    raw_results = pdf_engine.search(query)

    results = []

    for item in raw_results:

        results.append({
            "id": item["id"],
            "filename": item["filename"],
            "pages": item["pages"],
            "size": item["size"],
            "preview": item["preview"],
            "document_type": item["document_type"],
            "thumbnail": f"{base_url}/thumbnails/{item['thumbnail']}",
            "file": f"{base_url}/pdfs/{item['filename']}",
            "score": item.get("score", 0)
        })

    return jsonify(results)


# =====================================================
# PDF Upload API
# =====================================================

@app.route("/pdf_upload", methods=["POST"])
def pdf_upload():

    files = request.files.getlist("files")

    if not files:
        return jsonify({
            "status": "error",
            "message": "No files selected"
        }), 400

    results = []

    for file in files:

        if file.filename == "":
            results.append({
                "filename": "",
                "status": "error",
                "message": "Empty filename"
            })
            continue

        if not allowed_file(file.filename, PDF_EXTENSIONS):
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": "Unsupported file type for PDF upload"
            })
            continue

        upload_path = UPLOAD_FOLDER / file.filename

        file.save(upload_path)

        try:
            result = pdf_upload_processor.process(upload_path)
            results.append(result)

        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": f"PDF processing failed : {e}"
            })

    # Reload PDF search engine once after the whole batch
    pdf_engine.reload_data()

    overall_status = (
        "success"
        if any(item.get("status") == "success" for item in results)
        else "error"
    )

    status_code = 200 if overall_status == "success" else 400

    return jsonify({
        "status": overall_status,
        "results": results
    }), status_code


# =====================================================
# Videos API
# =====================================================

@app.route("/videos", methods=["GET"])
def videos():

    base_url = request.host_url.rstrip("/")

    metadata = load_json_safe(VIDEO_METADATA_FILE, default=[])

    videos = []

    for index, item in enumerate(metadata):

        # -----------------------------------------------------
        # Defensive: an entry uploaded through /video_upload
        # before the id fix (or any future malformed entry)
        # must not be able to 500 this endpoint for everyone.
        # Skip anything missing what we actually need to render
        # it, and fall back to an index-based id when "id" is
        # absent so the item still shows up in the gallery.
        # -----------------------------------------------------
        if "filename" not in item or "thumbnail" not in item:
            print(f"⚠️ Skipping video metadata entry {index} : missing 'filename' or 'thumbnail'")
            continue

        thumbnail_name = Path(item["thumbnail"]).name

        video_id = item.get("id", index)

        videos.append({
            "id": video_id,
            "filename": item["filename"],
            "duration": item.get("duration", ""),
            "size": item.get("size", 0),
            "thumbnail": f"{base_url}/video_frames/{thumbnail_name}",
            "video": f"{base_url}/videos/{item['filename']}",
            "caption": item.get("caption", ""),
            "objects": item.get("objects", []),
            "tags": item.get("tags", [])
        })

    return jsonify(videos)


# =====================================================
# Background Video Processing Worker
# =====================================================

def _process_video_in_background(upload_path, filename):

    with VIDEO_UPLOAD_STATUS_LOCK:
        VIDEO_UPLOAD_STATUS[filename] = {"status": "processing"}

    try:
        result = video_upload_processor.process(upload_path)

        # Reload latest metadata so gallery/search/dashboard pick it up
        video_engine.reload_data()

        with VIDEO_UPLOAD_STATUS_LOCK:
            VIDEO_UPLOAD_STATUS[filename] = {
                "status": "success",
                "result": result
            }

    except Exception as e:
        with VIDEO_UPLOAD_STATUS_LOCK:
            VIDEO_UPLOAD_STATUS[filename] = {
                "status": "error",
                "message": f"Video processing failed : {e}"
            }


# =====================================================
# Video Upload API
# =====================================================

@app.route("/video_upload", methods=["POST"])
def video_upload():

    files = request.files.getlist("files")

    if not files:
        return jsonify({
            "status": "error",
            "message": "No files selected"
        }), 400

    accepted = []
    rejected = []

    for file in files:

        if file.filename == "":
            rejected.append({
                "filename": "",
                "message": "Empty filename"
            })
            continue

        if not allowed_file(file.filename, VIDEO_EXTENSIONS):
            rejected.append({
                "filename": file.filename,
                "message": "Unsupported file type for video upload"
            })
            continue

        upload_path = UPLOAD_FOLDER / file.filename

        file.save(upload_path)

        # -----------------------------------------
        # Kick Off Processing In The Background
        # -----------------------------------------
        thread = threading.Thread(
            target=_process_video_in_background,
            args=(upload_path, file.filename),
            daemon=True
        )
        thread.start()

        accepted.append(file.filename)

    return jsonify({
        "status": "processing" if accepted else "error",
        "accepted": accepted,
        "rejected": rejected,
        "message": f"{len(accepted)} video(s) uploaded, processing in background."
    }), (202 if accepted else 400)


# =====================================================
# Video Upload Status API (Polling)
# =====================================================

@app.route("/video_upload_status/<filename>", methods=["GET"])
def video_upload_status(filename):

    with VIDEO_UPLOAD_STATUS_LOCK:
        status = VIDEO_UPLOAD_STATUS.get(filename)

    if status is None:
        return jsonify({
            "status": "unknown",
            "message": "No upload found for this filename"
        }), 404

    return jsonify(status)


# =====================================================
# Video Search API
# =====================================================

@app.route("/video_search", methods=["POST"])
def video_search():

    data = request.get_json(silent=True) or {}

    query = data.get("query", "").strip()

    if query == "":
        return jsonify([])

    base_url = request.host_url.rstrip("/")

    video_engine.reload_data()

    raw_results = video_engine.search(query)

    results = []

    for item in raw_results:

        results.append({
            "filename": item["filename"],
            "thumbnail": f"{base_url}/video_frames/{item['thumbnail']}",
            "video": f"{base_url}/videos/{item['filename']}",
            "duration": item.get("duration", ""),
            "objects": item.get("objects", []),
            "caption": item.get("caption", ""),
            "tags": item.get("tags", []),
            "score": item.get("score", 0)
        })

    return jsonify(results)


# =====================================================
# Serve Images
# =====================================================

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


# =====================================================
# Serve PDF Thumbnails
# =====================================================

@app.route("/thumbnails/<filename>")
def thumbnails(filename):
    return send_from_directory(THUMBNAILS_FOLDER, filename)


# =====================================================
# Serve PDFs
# =====================================================

@app.route("/pdfs/<filename>")
def pdfs(filename):
    return send_from_directory(DOCUMENTS_FOLDER, filename, as_attachment=False)


# =====================================================
# Serve Videos
# =====================================================

@app.route("/videos/<filename>")
def videos_file(filename):
    return send_from_directory(VIDEOS_FOLDER, filename, as_attachment=False)


# =====================================================
# Serve Video Frames
# =====================================================

@app.route("/video_frames/<filename>")
def video_frames(filename):
    return send_from_directory(VIDEO_THUMBNAILS_FOLDER, filename)


# =====================================================
# Delete Image
# =====================================================

@app.route("/delete/<filename>", methods=["DELETE"])
def delete_image(filename):

    image_path = IMAGE_FOLDER / filename

    if not image_path.exists():
        return jsonify({
            "status": "error",
            "message": "Image not found"
        }), 404

    os.remove(image_path)

    metadata = load_json_safe(METADATA_FILE, default=[])

    delete_index = None

    for i, item in enumerate(metadata):
        if item["filename"] == filename:
            delete_index = i
            break

    if delete_index is None:
        return jsonify({
            "status": "error",
            "message": "Metadata not found"
        }), 404

    metadata.pop(delete_index)

    save_json_safe(METADATA_FILE, metadata)

    embedding_file = BACKEND_DIR / "embeddings" / "image_embeddings.npy"

    embeddings = load_embeddings_safe(embedding_file)

    if embeddings is not None and delete_index < len(embeddings):
        embeddings = np.delete(embeddings, delete_index, axis=0)
        np.save(embedding_file, embeddings)

    engine.reload_data()

    return jsonify({
        "status": "success",
        "message": "Image deleted"
    })


# =====================================================
# Delete PDF
# =====================================================

@app.route("/delete_pdf/<filename>", methods=["DELETE"])
def delete_pdf(filename):

    pdf_path = DOCUMENTS_FOLDER / filename

    if not pdf_path.exists():
        return jsonify({
            "status": "error",
            "message": "PDF not found"
        }), 404

    metadata = load_json_safe(PDF_METADATA_FILE, default=[])

    delete_index = None

    thumbnail = None

    text_file = None

    for i, item in enumerate(metadata):
        if item["filename"] == filename:
            delete_index = i
            thumbnail = Path(item["thumbnail"])
            text_file = Path(item["text_file"])
            break

    if delete_index is None:
        return jsonify({
            "status": "error",
            "message": "Metadata not found"
        }), 404

    if pdf_path.exists():
        os.remove(pdf_path)

    if thumbnail and thumbnail.exists():
        os.remove(thumbnail)

    if text_file and text_file.exists():
        os.remove(text_file)

    metadata.pop(delete_index)

    save_json_safe(PDF_METADATA_FILE, metadata)

    embedding_file = BACKEND_DIR / "embeddings" / "pdf_embeddings.npy"

    embeddings = load_embeddings_safe(embedding_file)

    if embeddings is not None and delete_index < len(embeddings):
        embeddings = np.delete(embeddings, delete_index, axis=0)
        np.save(embedding_file, embeddings)

    pdf_engine.reload_data()

    return jsonify({
        "status": "success",
        "message": "PDF deleted"
    })


# =====================================================
# Delete Video
# =====================================================

@app.route("/delete_video/<filename>", methods=["DELETE"])
def delete_video(filename):

    video_path = VIDEOS_FOLDER / filename

    if not video_path.exists():
        return jsonify({
            "status": "error",
            "message": "Video not found"
        }), 404

    metadata = load_json_safe(VIDEO_METADATA_FILE, default=[])

    delete_index = None

    thumbnail = None

    for i, item in enumerate(metadata):
        if item["filename"] == filename:
            delete_index = i
            thumbnail = Path(item["thumbnail"])
            break

    if delete_index is None:
        return jsonify({
            "status": "error",
            "message": "Metadata not found"
        }), 404

    if video_path.exists():
        os.remove(video_path)

    if thumbnail and thumbnail.exists():
        os.remove(thumbnail)

    metadata.pop(delete_index)

    save_json_safe(VIDEO_METADATA_FILE, metadata)

    embedding_file = BACKEND_DIR / "embeddings" / "video_embeddings.npy"

    embeddings = load_embeddings_safe(embedding_file)

    if embeddings is not None and delete_index < len(embeddings):
        embeddings = np.delete(embeddings, delete_index, axis=0)
        np.save(embedding_file, embeddings)

    video_engine.reload_data()

    return jsonify({
        "status": "success",
        "message": "Video deleted"
    })


# =====================================================
# Run Server
# =====================================================

if __name__ == "__main__":

    print("\n========================================")
    print("      OmniRecall AI Backend Started")
    print("========================================")

    print(f"Images Folder     : {IMAGE_FOLDER}")
    print(f"Videos Folder     : {VIDEOS_FOLDER}")
    print(f"Documents Folder  : {DOCUMENTS_FOLDER}")
    print(f"Uploads Folder    : {UPLOAD_FOLDER}")

    print("----------------------------------------")

    print(f"Image Metadata    : {METADATA_FILE}")
    print(f"PDF Metadata      : {PDF_METADATA_FILE}")
    print(f"Video Metadata    : {VIDEO_METADATA_FILE}")

    print("========================================\n")

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)