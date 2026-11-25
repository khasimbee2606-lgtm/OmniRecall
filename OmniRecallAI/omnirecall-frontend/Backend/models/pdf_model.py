import fitz
import numpy as np
from PIL import Image
import re
from pathlib import Path
from models.registry import get_clip_model


class PDFModel:

    def __init__(self):

        self.clip = get_clip_model()

    # =====================================================
    # Extract PDF Text
    # =====================================================
    def extract_text(self, pdf_path):

        document = fitz.open(pdf_path)

        full_text = ""

        page_count = len(document)

        for page in document:

            text = page.get_text()

            if text:
                full_text += text + "\n"

        document.close()

        return full_text, page_count

    # =====================================================
    # Generate Thumbnail
    # =====================================================
    def generate_thumbnail(self, pdf_path, thumbnail_path):

        document = fitz.open(pdf_path)

        page = document.load_page(0)

        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        image.thumbnail((350, 450))

        image.save(thumbnail_path)

        document.close()

    # =====================================================
    # Preprocess Text
    # =====================================================
    def preprocess_text(self, text):

        text = text.lower()

        text = re.sub(r"\s+", " ", text)

        text = re.sub(r"[^\w\s]", "", text)

        return text.strip()

    # =====================================================
    # Generate Preview
    # =====================================================
    def generate_preview(self, text, length=250):

        if len(text) <= length:
            return text

        return text[:length] + "..."

    # =====================================================
    # Detect Document Type
    # =====================================================
    def detect_document_type(self, text):

        text = text.lower()

        if "aadhaar" in text or "government of india" in text:
            return "Identity Document"

        elif "permanent account number" in text or "income tax" in text:
            return "Identity Document"

        elif "resume" in text or "curriculum vitae" in text:
            return "Resume"

        elif "hall ticket" in text:
            return "Education"

        elif "bank statement" in text:
            return "Bank Statement"

        elif "certificate" in text:
            return "Certificate"

        elif "abstract" in text or "introduction" in text:
            return "Study Material"

        return "Other"

    # =====================================================
    # Generate Embedding
    # -----------------------------------------------------
    # CLIP's text encoder has a fixed context length
    # (77 tokens, roughly 50-60 words) — passing the entire
    # document text in one call silently truncates almost
    # everything past the opening lines. Instead, the text
    # is split into small chunks, each chunk is embedded
    # separately, and the results are mean-pooled and
    # re-normalized into a single document-level embedding.
    #
    # max_chunks caps how much of the document contributes to
    # the *semantic* embedding (exact keyword/content search in
    # pdf_search.py always reads the full extracted text
    # regardless of this cap). Raised from 25 -> 60 chunks
    # (~1250 -> ~3000 words) so longer documents get broader
    # semantic coverage; still bounded so very large PDFs don't
    # make uploads slow.
    # =====================================================
    def generate_embedding(self, text, chunk_size=50, max_chunks=60):

        words = text.split()

        if not words:
            # Empty document — fall back to embedding an empty string
            # rather than crashing.
            return self.clip.encode_text("")

        # -----------------------------------------
        # Split Into CLIP-Safe Chunks
        # -----------------------------------------
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))

            if len(chunks) >= max_chunks:
                break

        # -----------------------------------------
        # Embed Each Chunk
        # -----------------------------------------
        chunk_embeddings = []

        for chunk in chunks:
            try:
                chunk_embedding = self.clip.encode_text(chunk)
                chunk_embeddings.append(chunk_embedding)

            except Exception as e:
                print(f"PDF chunk embedding warning : {e}")

        if not chunk_embeddings:
            # All chunk embeddings failed — fall back to a short
            # single-call embedding rather than raising.
            return self.clip.encode_text(text[:200])

        # -----------------------------------------
        # Mean-Pool And Re-Normalize
        # -----------------------------------------
        stacked = np.stack(chunk_embeddings, axis=0)

        embedding = np.mean(stacked, axis=0)

        norm = np.linalg.norm(embedding)

        if norm > 0:
            embedding = embedding / norm

        return embedding.astype(np.float32)

    # =====================================================
    # Process PDF
    # =====================================================
    def process_pdf(self, pdf_path):

        pdf_path = Path(pdf_path)

        raw_text, page_count = self.extract_text(pdf_path)

        clean_text = self.preprocess_text(raw_text)

        preview = self.generate_preview(clean_text)

        document_type = self.detect_document_type(clean_text)

        thumbnail_path = pdf_path.parent.parent / "thumbnails" / f"{pdf_path.stem}.png"

        self.generate_thumbnail(pdf_path, thumbnail_path)

        embedding = self.generate_embedding(clean_text)

        return {
            "filename": pdf_path.name,
            "content": clean_text,
            "preview": preview,
            "pages": page_count,
            "document_type": document_type,
            "thumbnail": str(thumbnail_path),
            "embedding": embedding
        }