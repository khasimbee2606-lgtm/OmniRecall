from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

import os

from config import (
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS
)

upload_bp = Blueprint("upload", __name__)


def allowed_file(filename):

    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@upload_bp.route("/upload", methods=["POST"])
def upload_image():

    if "image" not in request.files:

        return jsonify({

            "success": False,
            "message": "No image uploaded."

        }), 400

    file = request.files["image"]

    if file.filename == "":

        return jsonify({

            "success": False,
            "message": "Empty filename."

        }), 400

    if not allowed_file(file.filename):

        return jsonify({

            "success": False,
            "message": "Invalid file type."

        }), 400

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    return jsonify({

        "success": True,

        "filename": filename,

        "path": filepath

    })