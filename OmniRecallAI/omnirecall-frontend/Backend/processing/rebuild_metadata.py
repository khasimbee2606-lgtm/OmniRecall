import sys
import json
from pathlib import Path

# ==========================================
# Backend Path
# ==========================================

BACKEND_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BACKEND_DIR))

# ==========================================

from utils.tag_generator import generate_tags

# ==========================================

METADATA_FILE = BACKEND_DIR / "metadata" / "metadata.json"

# ==========================================

with open(METADATA_FILE, "r") as file:

    metadata = json.load(file)

new_metadata = []

for image in metadata:

    filename = image.get("filename", "")

    objects = image.get("objects", [])

    tags = generate_tags(filename, objects)

    searchable = " ".join(
        [
            filename.lower(),
            " ".join(objects).lower(),
            " ".join(tags).lower()
        ]
    )

    new_metadata.append({

        "filename": filename,

        "objects": objects,

        "tags": tags,

        "searchable": searchable,

        "favorite": image.get("favorite", False),

        "upload_date": image.get("upload_date", "")

    })

with open(METADATA_FILE, "w") as file:

    json.dump(new_metadata, file, indent=4)

print("\n====================================")
print("Metadata Rebuilt Successfully")
print(f"Updated {len(new_metadata)} Images")
print("====================================")