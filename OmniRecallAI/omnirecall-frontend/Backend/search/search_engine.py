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

METADATA_FILE = BACKEND_DIR / "metadata" / "metadata.json"

EMBEDDING_FILE = BACKEND_DIR / "embeddings" / "image_embeddings.npy"

# =====================================================
# Search Engine
# =====================================================


class SearchEngine:

    def __init__(self):

        self.clip = get_clip_model()

        # ---------------------------------------------
        # Load Metadata
        # ---------------------------------------------
        if METADATA_FILE.exists():
            with open(METADATA_FILE, "r", encoding="utf-8") as file:
                self.metadata = json.load(file)

        else:
            self.metadata = []

        # ---------------------------------------------
        # Load Embeddings
        # ---------------------------------------------
        if EMBEDDING_FILE.exists():
            self.embeddings = np.load(EMBEDDING_FILE, allow_pickle=False)

            # Handle single-image embedding file
            if self.embeddings.ndim == 1:
                self.embeddings = self.embeddings.reshape(1, -1)

        else:
            self.embeddings = np.array([])

        print(f"\nLoaded {len(self.metadata)} images.")

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

            # Handle single-image embedding file
            if self.embeddings.ndim == 1:
                self.embeddings = self.embeddings.reshape(1, -1)

        else:
            self.embeddings = np.array([])

        print("\n✓ Search Engine Reloaded")
        print(f"Loaded {len(self.metadata)} images.")

    # =====================================================
    # Natural Language Preprocessing
    # =====================================================
    def preprocess_query(self, query):

        query = query.lower()

        query = re.sub(r"[^\w\s]", "", query)

        stop_words = {
            "show",
            "showing",
            "display",
            "displaying",
            "find",
            "search",
            "photo",
            "photos",
            "picture",
            "pictures",
            "image",
            "images",
            "my",
            "me",
            "the",
            "a",
            "an",
            "of",
            "with",
            "all",
            "please",
            "give",
            "get"
        }

        words = []

        for word in query.split():
            if word not in stop_words:
                words.append(word)

        return " ".join(words)

    # =====================================================
    # Query Expansion
    # =====================================================
    def expand_query(self, query):

        synonym_map = {

            # =====================================================
            # PEOPLE
            # =====================================================

            "friend": [
                "friends", "group", "people", "person", "team",
                "family", "classmate", "classmates", "buddy",
                "pal", "gang", "crew", "selfie"
            ],

            "friends": [
                "friends", "group", "people", "person", "team",
                "family", "classmate", "classmates", "buddy",
                "pal", "gang", "crew", "selfie"
            ],

            "person": [
                "people", "human", "man", "woman",
                "individual", "someone",
                "boy", "girl", "friends",
                "family", "friend"
            ],

            "people": [
                "person", "human",
                "group", "friends",
                "family"
            ],

            "family": [
                "parents", "mother", "father",
                "mom", "dad",
                "brother", "sister",
                "children",
                "relatives",
                "friends"
            ],

            # =====================================================
            # EDUCATION
            # =====================================================

            "college": [
                "campus",
                "student",
                "students",
                "education",
                "graduation",
                "classroom",
                "university",
                "classmate",
                "degree",
                "lecture"
            ],

            "graduation": [
                "college",
                "campus",
                "student",
                "education",
                "degree",
                "convocation",
                "certificate",
                "cap",
                "gown"
            ],

            "school": [
                "education",
                "student",
                "classroom",
                "teacher",
                "campus"
            ],

            # =====================================================
            # FLOWERS
            # =====================================================

            "flower": [
                "flowers",
                "garden",
                "nature",
                "plant",
                "rose",
                "lotus",
                "sunflower",
                "jasmine",
                "bouquet",
                "blossom",
                "petals",
                "green"
            ],

            "flowers": [
                "flower",
                "garden",
                "nature",
                "plant",
                "rose",
                "lotus",
                "sunflower",
                "jasmine",
                "bouquet",
                "blossom",
                "petals",
                "green"
            ],

            "plant": [
                "flower",
                "flowers",
                "garden",
                "nature",
                "tree",
                "leaf",
                "green"
            ],

            # =====================================================
            # ANIMALS
            # =====================================================

            "dog": [
                "animal",
                "puppy",
                "canine",
                "cute"
            ],

            "cat": [
                "kitten",
                "pet",
                "animal",
                "feline"
            ],

            "bird": [
                "birds",
                "parrot",
                "sparrow",
                "crow",
                "eagle",
                "pigeon",
                "peacock"
            ],

            "animal": [
                "dog",
                "cat",
                "bird",
                "horse",
                "cow",
                "elephant",
                "pet",
                "wildlife"
            ],

            # =====================================================
            # OFFICE
            # =====================================================

            "office": [
                "computer",
                "laptop",
                "work",
                "meeting",
                "employee",
                "company",
                "business",
                "desk",
                "workspace",
                "coding"
            ],

            "computer": [
                "laptop",
                "office",
                "desktop",
                "coding",
                "technology"
            ],

            "laptop": [
                "computer",
                "office",
                "coding",
                "developer",
                "technology",
                "work"
            ],

            # =====================================================
            # EVENTS
            # =====================================================

            "birthday": [
                "cake",
                "celebration",
                "party",
                "balloons",
                "friends",
                "family",
                "candles",
                "gift"
            ],

            "wedding": [
                "marriage",
                "bride",
                "groom",
                "ceremony",
                "couple",
                "family",
                "celebration"
            ],

            "festival": [
                "celebration",
                "event",
                "holiday",
                "family",
                "tradition"
            ],

            # =====================================================
            # TRAVEL
            # =====================================================

            "beach": [
                "sea",
                "ocean",
                "vacation",
                "holiday",
                "travel",
                "sand",
                "shore",
                "waves"
            ],

            "mountain": [
                "hill",
                "nature",
                "travel",
                "trekking",
                "adventure"
            ],

            "travel": [
                "trip",
                "tour",
                "vacation",
                "journey",
                "holiday"
            ],

            # =====================================================
            # DOCUMENTS
            # =====================================================

            "passport": [
                "document",
                "id",
                "identity",
                "travel",
                "government"
            ],

            "aadhaar": [
                "aadhar",
                "document",
                "id",
                "identity",
                "government",
                "card"
            ],

            "certificate": [
                "document",
                "degree",
                "education",
                "graduation"
            ],

            # =====================================================
            # RELIGIOUS
            # =====================================================

            "temple": [
                "god",
                "religion",
                "prayer",
                "spiritual",
                "worship",
                "holy"
            ],

            "church": [
                "religion",
                "god",
                "prayer",
                "holy"
            ],

            "mosque": [
                "religion",
                "prayer",
                "allah",
                "holy"
            ],

            # =====================================================
            # VEHICLES
            # =====================================================

            "car": [
                "vehicle",
                "travel",
                "road",
                "drive"
            ],

            "bike": [
                "motorcycle",
                "ride",
                "vehicle"
            ],

            "bus": [
                "transport",
                "vehicle",
                "travel"
            ],

            "train": [
                "railway",
                "travel",
                "transport"
            ],

            "airplane": [
                "flight",
                "airport",
                "travel"
            ],

            # =====================================================
            # NATURE
            # =====================================================

            "tree": [
                "trees",
                "forest",
                "woods",
                "nature",
                "green",
                "leaf",
                "branches",
                "park"
            ],

            "forest": [
                "trees",
                "woods",
                "nature",
                "green",
                "jungle",
                "wildlife"
            ],

            "river": [
                "water",
                "stream",
                "lake",
                "nature",
                "bridge",
                "shore"
            ],

            "lake": [
                "water",
                "river",
                "pond",
                "nature",
                "boat"
            ],

            "waterfall": [
                "nature",
                "water",
                "river",
                "travel",
                "mountain"
            ],

            "garden": [
                "flowers",
                "plants",
                "nature",
                "green",
                "park"
            ],

            "sky": [
                "cloud",
                "sun",
                "blue",
                "nature",
                "sunset",
                "sunrise"
            ],

            "sunset": [
                "evening",
                "sky",
                "orange",
                "nature",
                "sun"
            ],

            "sunrise": [
                "morning",
                "sky",
                "sun",
                "nature"
            ],

            # =====================================================
            # WEATHER
            # =====================================================

            "rain": [
                "rainy",
                "cloud",
                "storm",
                "umbrella",
                "water",
                "monsoon"
            ],

            "sun": [
                "sunny",
                "bright",
                "day",
                "light",
                "summer"
            ],

            "cloud": [
                "sky",
                "rain",
                "weather"
            ],

            "snow": [
                "winter",
                "ice",
                "cold"
            ],

            "winter": [
                "cold",
                "snow",
                "fog"
            ],

            "summer": [
                "hot",
                "sun",
                "vacation"
            ],

            # =====================================================
            # EMOTIONS
            # =====================================================

            "happy": [
                "smile",
                "smiling",
                "joy",
                "celebration",
                "fun",
                "laugh",
                "excited"
            ],

            "sad": [
                "cry",
                "unhappy",
                "upset"
            ],

            "love": [
                "heart",
                "romantic",
                "couple",
                "affection"
            ],

            "fun": [
                "happy",
                "friends",
                "party",
                "celebration"
            ],

            # =====================================================
            # FOOD
            # =====================================================

            "food": [
                "meal",
                "restaurant",
                "lunch",
                "dinner",
                "breakfast",
                "snack"
            ],

            "cake": [
                "dessert",
                "sweet",
                "birthday",
                "celebration"
            ],

            "coffee": [
                "tea",
                "drink",
                "cafe"
            ],

            "restaurant": [
                "food",
                "meal",
                "cafe",
                "dining"
            ],

            # =====================================================
            # SPORTS
            # =====================================================

            "football": [
                "soccer",
                "sports",
                "match",
                "game"
            ],

            "cricket": [
                "bat",
                "ball",
                "sports",
                "match"
            ],

            "badminton": [
                "sports",
                "racket",
                "game"
            ],

            "gym": [
                "fitness",
                "exercise",
                "workout",
                "training"
            ],

            # =====================================================
            # HOME
            # =====================================================

            "house": [
                "home",
                "building",
                "residence",
                "family"
            ],

            "room": [
                "bedroom",
                "hall",
                "home",
                "interior"
            ],

            "kitchen": [
                "cooking",
                "food",
                "home"
            ],

            # =====================================================
            # TECHNOLOGY
            # =====================================================

            "phone": [
                "mobile",
                "smartphone",
                "cellphone"
            ],

            "camera": [
                "photo",
                "photography",
                "dslr",
                "picture"
            ],

            "internet": [
                "online",
                "wifi",
                "web"
            ],

            # =====================================================
            # CLOTHING
            # =====================================================

            "shirt": [
                "clothes",
                "dress",
                "fashion",
                "tshirt"
            ],

            "dress": [
                "clothes",
                "fashion",
                "gown"
            ],

            "shoes": [
                "footwear",
                "sneakers",
                "boots"
            ],

            # =====================================================
            # PLACES
            # =====================================================

            "party": [
                "celebration",
                "birthday",
                "friends",
                "music"
            ],

            "gift": [
                "present",
                "birthday",
                "celebration"
            ],

            "decoration": [
                "party",
                "festival",
                "celebration"
            ],

            "park": [
                "garden",
                "nature",
                "trees",
                "walking"
            ],

            "mall": [
                "shopping",
                "store",
                "market"
            ],

            "hotel": [
                "travel",
                "vacation",
                "stay"
            ],

            "airport": [
                "flight",
                "airplane",
                "travel"
            ],

            "station": [
                "train",
                "railway",
                "travel"
            ],

            # =====================================================
            # TIME
            # =====================================================

            "morning": [
                "sunrise",
                "day",
                "early"
            ],

            "afternoon": [
                "day",
                "noon"
            ],

            "evening": [
                "sunset",
                "night"
            ],

            "night": [
                "dark",
                "moon",
                "stars"
            ],

            # =====================================================
            # COLORS
            # =====================================================

            "red": [
                "crimson",
                "scarlet"
            ],

            "blue": [
                "sky",
                "ocean"
            ],

            "green": [
                "nature",
                "grass",
                "forest"
            ],

            "yellow": [
                "gold",
                "sunshine"
            ],

            "white": [
                "bright",
                "light"
            ],

            "black": [
                "dark",
                "shadow"
            ],

            # =====================================================
            # PEOPLE
            # =====================================================

            "baby": [
                "child",
                "kid",
                "infant"
            ],

            "child": [
                "kid",
                "baby",
                "children"
            ],

            "teacher": [
                "professor",
                "faculty",
                "education"
            ],

            "developer": [
                "programmer",
                "coding",
                "software",
                "computer"
            ]

        }

        expanded = []

        for word in query.split():

            expanded.append(word)

            if word in synonym_map:
                expanded.extend(synonym_map[word])

        return " ".join(list(dict.fromkeys(expanded)))

    # =====================================================
    # Word-Boundary Text Match
    # =====================================================
    # Plain "word in text" is a *substring* test, so a query
    # word like "cat" incorrectly matches inside unrelated
    # words such as "vacation" or "location" (both literally
    # contain the letters c-a-t). This wraps the word in \b
    # (regex word boundaries) so it only matches whole words,
    # while still matching a word inside a multi-word phrase
    # like "sports ball" or "cell phone" (spaces are already
    # word boundaries).
    # =====================================================
    def word_match(self, word, text):

        if not word or not text:
            return False

        pattern = r"\b" + re.escape(word) + r"\b"

        return re.search(pattern, text) is not None

    # =====================================================
    # Search
    # =====================================================
    def search(self, query, top_k=20):

        clean_query = self.preprocess_query(query)

        expanded_query = self.expand_query(clean_query)

        # ---------------------------------------------
        # Empty Query
        # ---------------------------------------------
        if expanded_query.strip() == "":
            return []

        # ---------------------------------------------
        # No Images
        # ---------------------------------------------
        if len(self.metadata) == 0:
            return []

        if len(self.embeddings) == 0:
            return []

        query_embedding = self.clip.encode_text(expanded_query)

        results = []

        for index, image_embedding in enumerate(self.embeddings):

            # -----------------------------------------
            # Prevent Metadata / Embedding Mismatch
            # -----------------------------------------
            if index >= len(self.metadata):
                continue

            similarity = float(np.dot(query_embedding, image_embedding))

            # ---------------------------------------------
            # Ignore Very Weak Matches
            # ---------------------------------------------
            if similarity < 0.18:
                continue

            score = similarity * 100

            matched = False

            semantic_match = similarity >= 0.28

            metadata = self.metadata[index]

            confidence = metadata.get("confidence", [])

            filename = metadata["filename"].lower()

            objects = [obj.lower() for obj in metadata.get("objects", [])]

            tags = [tag.lower() for tag in metadata.get("tags", [])]

            caption = metadata.get("caption", "").lower()

            searchable = metadata.get("searchable", "").lower()

            query_words = expanded_query.split()

            match_count = 0

            # ---------------------------------------------
            # Semantic Bonus
            # ---------------------------------------------
            for word in query_words:

                if self.word_match(word, searchable):
                    score += 8

                if self.word_match(word, caption):
                    score += 10

            # ---------------------------------------------
            # Keyword Boosting
            # ---------------------------------------------
            for word in query_words:

                # -----------------------------------------
                # Filename
                # -----------------------------------------
                if self.word_match(word, filename):
                    score += 50
                    matched = True
                    match_count += 1

                # -----------------------------------------
                # Objects
                # Confidence bonus only applies to objects
                # that actually match the query word, not
                # to every object detected in the image.
                # -----------------------------------------
                for obj_index, obj in enumerate(objects):

                    obj_confidence = (
                        confidence[obj_index]
                        if obj_index < len(confidence)
                        else 0
                    )

                    if word == obj:
                        score += 50 + (obj_confidence * 10)
                        matched = True
                        match_count += 1

                    elif self.word_match(word, obj):
                        score += 30 + (obj_confidence * 10)
                        matched = True
                        match_count += 1

                # -----------------------------------------
                # Tags
                # -----------------------------------------
                for tag in tags:

                    if word == tag:
                        score += 40
                        matched = True
                        match_count += 1

                    elif self.word_match(word, tag):
                        score += 25
                        matched = True
                        match_count += 1

                # -----------------------------------------
                # Caption
                # -----------------------------------------
                if self.word_match(word, caption):
                    score += 20
                    matched = True

                # -----------------------------------------
                # Searchable Text
                # -----------------------------------------
                if self.word_match(word, searchable):
                    score += 15
                    matched = True

            # ---------------------------------------------
            # Multiple Match Bonus
            # ---------------------------------------------
            score += match_count * 6

            # ---------------------------------------------
            # Reject Weak Matches
            # ---------------------------------------------
            if not matched and not semantic_match:
                continue

            results.append({
                "filename": metadata["filename"],
                "objects": metadata["objects"],
                "score": round(score, 2)
            })

        # ---------------------------------------------
        # Sort Results
        # ---------------------------------------------
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    engine = SearchEngine()

    while True:

        print("\n--------------------------------")

        query = input("Search Image : ").strip()

        if query.lower() == "exit":
            break

        results = engine.search(query)

        print("\n========================================")
        print("Top Matches")
        print("========================================")

        if len(results) == 0:
            print("No matching images found.")

        else:
            for i, image in enumerate(results, start=1):
                print(f"\n{i}. {image['filename']}")
                print(f"Score   : {image['score']}")
                print(f"Objects : {image['objects']}")
                print("-" * 40)

        print("\n========================================")