import sys
import json
import re
import numpy as np
from pathlib import Path

# =====================================================
# Backend Path
# =====================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BACKEND_DIR))

from models.registry import get_clip_model

# =====================================================
# Files
# =====================================================

METADATA_FILE = BACKEND_DIR / "metadata" / "pdf_metadata.json"
EMBEDDING_FILE = BACKEND_DIR / "embeddings" / "pdf_embeddings.npy"


class PDFSearchEngine:

    # =====================================================
    # Constructor
    # =====================================================
    def __init__(self):

        self.clip = get_clip_model()

        self.reload_data()

    # =====================================================
    # Reload Metadata & Embeddings
    # =====================================================
    def reload_data(self):

        if METADATA_FILE.exists():
            with open(METADATA_FILE, "r", encoding="utf-8") as file:
                self.metadata = json.load(file)

        else:
            self.metadata = []

        if EMBEDDING_FILE.exists():
            self.embeddings = np.load(EMBEDDING_FILE, allow_pickle=False)

            # Handle single-document embedding file
            if self.embeddings.ndim == 1:
                self.embeddings = self.embeddings.reshape(1, -1)

        else:
            self.embeddings = np.empty((0, 512))

    # =====================================================
    # PDF Search
    # =====================================================
    def search(self, query, top_k=20):

        query = query.lower().strip()

        if query == "":
            return []

        if len(self.metadata) == 0:
            return []

        if len(self.embeddings) == 0:
            return []

        # =================================================
        # Query Expansion (Synonyms)
        # =================================================
        synonym_map = {

            "genai": [
                "genai",
                "gen ai",
                "generative ai",
                "generative artificial intelligence"
            ],

            "ai": [
                "ai",
                "artificial intelligence",
                "machine intelligence"
            ],

            "ml": [
                "ml",
                "machine learning"
            ],

            "llm": [
                "llm",
                "large language model",
                "language model"
            ],

            "nlp": [
                "nlp",
                "natural language processing"
            ],

            "transformer": [
                "transformer",
                "encoder",
                "decoder",
                "attention",
                "attention mechanism"
            ],

            "resume": [
                "resume",
                "cv",
                "curriculum vitae"
            ],

            "aadhaar": [
                "aadhaar",
                "aadhar",
                "uidai",
                "government of india"
            ],

            "bank": [
                "bank",
                "statement",
                "transaction",
                "account"
            ],

            "certificate": [
                "certificate",
                "completion certificate",
                "provisional certificate"
            ],

            "hall ticket": [
                "hall ticket",
                "admit card"
            ]
        }

        # -----------------------------------------------
        # Build Keyword Set
        # -------------------------------------------------
        # Previously only the full query string was checked
        # against synonym_map, so a multi-word query (e.g.
        # "machine learning report") was only ever matched as
        # one exact phrase — a document containing "machine"
        # and "learning" (but not as a contiguous phrase)
        # scored zero on keyword matching. Now the full phrase
        # AND each individual word are matched, and synonym
        # expansion is applied to each of those too.
        # =================================================
        raw_keywords = {query}

        raw_keywords.update(query.split())

        keywords = set(raw_keywords)

        for word in raw_keywords:
            if word in synonym_map:
                keywords.update(synonym_map[word])

        keywords = list(keywords)

        # Encode search query
        query_embedding = self.clip.encode_text(query)

        results = []

        # =================================================
        # Search Every PDF
        # =================================================
        for index, item in enumerate(self.metadata):

            # -----------------------------------------
            # Prevent Metadata / Embedding Mismatch
            # -----------------------------------------
            if index >= len(self.embeddings):
                continue

            # -----------------------------------------
            # Defensive: skip a malformed entry instead of
            # crashing the whole /pdf_search response. This
            # mirrors the same class of bug that crashed
            # /videos when an entry was missing "id".
            # -----------------------------------------
            required_keys = (
                "id", "filename", "preview",
                "document_type", "thumbnail", "text_file"
            )

            if not all(key in item for key in required_keys):
                print(f"⚠️ Skipping PDF metadata entry {index} : missing required field")
                continue

            score = 0

            keyword_found = False

            text = ""

            text_file = Path(item["text_file"])

            if text_file.exists():
                try:
                    with open(text_file, "r", encoding="utf-8") as file:
                        text = file.read().lower()

                except OSError as e:
                    print(f"⚠️ Failed to read {text_file.name} : {e}")

            filename = item["filename"].lower()

            preview = item["preview"].lower()

            doc_type = item["document_type"].lower()

            # =============================================
            # Exact Keyword Matching
            # =============================================
            for word in keywords:

                pattern = rf"\b{re.escape(word)}\b"

                # -----------------------------------------
                # Filename Match
                # -----------------------------------------
                if re.search(pattern, filename):
                    score += 500
                    keyword_found = True

                # -----------------------------------------
                # Document Type Match
                # -----------------------------------------
                if re.search(pattern, doc_type):
                    score += 200
                    keyword_found = True

                # -----------------------------------------
                # Preview Match
                # -----------------------------------------
                if re.search(pattern, preview):
                    score += 150
                    keyword_found = True

                # -----------------------------------------
                # PDF Content Match
                # -----------------------------------------
                matches = len(re.findall(pattern, text))

                if matches > 0:
                    score += matches * 50
                    keyword_found = True

            # =============================================
            # Semantic Similarity
            # =============================================
            similarity = float(np.dot(query_embedding, self.embeddings[index]))

            # Semantic bonus
            score += similarity * 25

            # =============================================
            # Ignore Irrelevant PDFs
            # =============================================
            # Skip if there is no keyword match and
            # semantic similarity is too low.
            if not keyword_found and similarity < 0.35:
                continue

            # Skip low scoring PDFs
            if score < 80:
                continue

            # =============================================
            # Build Result
            # =============================================
            thumbnail = Path(item["thumbnail"]).name

            results.append({
                "id": item["id"],
                "filename": item["filename"],
                "pages": item.get("pages", 0),
                "size": item.get("size", 0),
                "preview": item["preview"],
                "document_type": item["document_type"],
                "thumbnail": thumbnail,
                "score": round(score, 2)
            })

        # =================================================
        # Sort Results
        # =================================================
        results.sort(key=lambda x: x["score"], reverse=True)

        # =================================================
        # Remove Weak Results
        # =================================================
        MIN_SCORE = 80

        filtered_results = [
            item for item in results
            if item["score"] >= MIN_SCORE
        ]

        # =================================================
        # Return Top Results
        # =================================================
        return filtered_results[:top_k]