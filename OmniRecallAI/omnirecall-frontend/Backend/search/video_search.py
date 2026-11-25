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

METADATA_FILE = BACKEND_DIR / "metadata" / "video_metadata.json"

EMBEDDING_FILE = BACKEND_DIR / "embeddings" / "video_embeddings.npy"

# =====================================================
# Video Search Engine
# =====================================================


class VideoSearchEngine:

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

            # Handle single-video embedding file
            if self.embeddings.ndim == 1:
                self.embeddings = self.embeddings.reshape(1, -1)

        else:
            self.embeddings = np.array([])

        print(f"\nLoaded {len(self.metadata)} videos.")

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

            # Handle single-video embedding file
            if self.embeddings.ndim == 1:
                self.embeddings = self.embeddings.reshape(1, -1)

        else:
            self.embeddings = np.array([])

        print("\n✓ Video Search Engine Reloaded")
        print(f"Loaded {len(self.metadata)} videos.")

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
            "video",
            "videos",
            "movie",
            "movies",
            "clip",
            "clips",
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
                "puppy",
                "canine"
            ],

            "cat": [
                "kitten",
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
                "party",
                "balloons",
                "candles",
                "gift"
            ],

            "wedding": [
                "marriage",
                "bride",
                "groom",
                "ceremony",
                "couple"
            ],

            "festival": [
                "event",
                "holiday",
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
            ],

            # =====================================================
            # ACTIVITIES
            # =====================================================

            "dance": [
                "dancing",
                "dancer",
                "dancers",
                "choreography",
                "performance",
                "stage"
            ],

            "dancing": [
                "dance",
                "dancer",
                "dancers",
                "choreography",
                "performance",
                "stage"
            ],

            "walk": [
                "walking",
                "stroll",
                "strolling",
                "hike",
                "hiking",
                "path",
                "sidewalk",
                "street"
            ],

            "walking": [
                "walk",
                "stroll",
                "strolling",
                "hike",
                "hiking",
                "path",
                "sidewalk",
                "street"
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
    # word boundaries). Mirrors search_engine.py (image search)
    # so both engines behave the same way.
    # =====================================================
    def word_match(self, word, text):

        if not word or not text:
            return False

        # Only letters extend a word here — digits, underscores,
        # and punctuation all count as boundaries. Plain \b in
        # Python regex treats underscores AND digits as "word"
        # characters, so it silently fails to match a word like
        # "graduation" inside real-world filenames such as
        # "graduation_2023.mp4" or "graduation2023.mp4" (both
        # extremely common naming patterns), since there's no
        # \b transition between "graduation" and "_"/"2". This
        # still blocks "cat" from matching inside "vacation"
        # (letters on both sides), which is what \b was added
        # to prevent in the first place.
        pattern = r"(?<![a-z])" + re.escape(word) + r"(?![a-z])"

        return re.search(pattern, text) is not None

    # =====================================================
    # Inflection Check (dance / dancing / dancer / dancers)
    # =====================================================
    # expand_query() adds two very different kinds of words
    # under the same flat list: real synonyms/related concepts
    # ("mountain" -> "adventure") AND plain inflected forms of
    # the word the user typed ("dance" -> "dancing", "dancer").
    # Inflected forms are NOT loosely related — they're the same
    # word — so they should carry full weight, not the reduced
    # SYNONYM_WEIGHT used for genuinely different concepts.
    #
    # This uses a generic prefix-overlap check instead of a
    # fixed suffix table (-ing/-er/-s/...) so it isn't tied to
    # a hardcoded list of English endings: if one word is a
    # prefix of the other and the extra tail is short (<=4
    # chars), they're treated as the same underlying word.
    # =====================================================
    def _drop_silent_e(self, word):

        # "dance" -> "danc" so it lines up with "dancing"/"dancer",
        # which drop the trailing "e" before adding their suffix.
        if word.endswith("e") and len(word) > 3:
            return word[:-1]

        return word

    def is_word_variant(self, word, original_words):

        if word in original_words:
            return True

        word_candidates = {word, self._drop_silent_e(word)}

        for original in original_words:

            original_candidates = {original, self._drop_silent_e(original)}

            for w in word_candidates:

                for o in original_candidates:

                    if len(w) <= len(o):
                        shorter, longer = w, o
                    else:
                        shorter, longer = o, w

                    if len(shorter) < 3:
                        continue

                    if longer.startswith(shorter) and (len(longer) - len(shorter)) <= 4:
                        return True

        return False

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
        # No Videos
        # ---------------------------------------------
        if len(self.metadata) == 0:
            return []

        if len(self.embeddings) == 0:
            return []

        # ---------------------------------------------
        # CLIP Text Embedding
        # -----------------------------------------------
        # Uses the clean, unexpanded query — not the
        # synonym-expanded one. Encoding a synonym-stuffed
        # string ("office computer laptop work meeting...")
        # dilutes CLIP's understanding of what was actually
        # asked for. The expanded form is still used below,
        # but only for keyword/tag/caption matching, which is
        # what it was built for.
        # ---------------------------------------------
        query_embedding = self.clip.encode_text(clean_query)

        query_words = expanded_query.split()

        # ---------------------------------------------
        # Literal / Variant vs Loose-Synonym Words
        # -----------------------------------------------
        # A query word gets full weight (1.0) if it's something
        # the user actually typed, OR a simple inflected form of
        # it (dance/dancing/dancer — see is_word_variant). Every
        # other word expand_query() added is a genuinely
        # different but related concept ("mountain" -> "travel")
        # and gets a much smaller weight, since those are shared
        # across many unrelated categories.
        # ---------------------------------------------
        original_words = set(clean_query.split())

        SYNONYM_WEIGHT = 0.35

        # ---------------------------------------------
        # Per-Word Match Strength (not per-field)
        # -----------------------------------------------
        # metadata fields overlap heavily — "searchable" is
        # typically a concatenation of tags + caption + objects,
        # so a single shared word (e.g. "travel", appearing in
        # both "mountain"'s and "beach"'s synonym lists) could
        # previously be counted 2-3 times over just because it
        # showed up in multiple fields that all describe the
        # same underlying fact. That let one loosely-related
        # word alone cross the match threshold.
        #
        # Fixed here: for each query word, only its STRONGEST
        # single field hit counts (FIELD_FACTOR below), added to
        # match_strength once. A video only counts as a genuine
        # keyword match once the sum across DISTINCT words clears
        # MATCH_STRENGTH_THRESHOLD — so either one strong literal
        # hit, or several independently-corroborating words, not
        # one word echoed across overlapping fields.
        # ---------------------------------------------
        FIELD_FACTOR = {
            "filename": 1.0,
            "object_exact": 1.0,
            "object_partial": 0.85,
            "tag_exact": 1.0,
            "tag_partial": 0.75,
            "caption": 0.85,
            "searchable": 0.75,
        }

        MATCH_STRENGTH_THRESHOLD = 0.85

        # ---------------------------------------------
        # Standalone Semantic Bar
        # -----------------------------------------------
        # CLIP similarity alone (no keyword overlap at all) can
        # still let visually-similar-but-different scenes through
        # — e.g. a beach and a snow scene both being wide open,
        # bright, textured terrain under open sky can push
        # similarity just over 0.28 despite being different
        # subjects. So similarity between MIN_ABS_SIMILARITY and
        # STRONG_SEMANTIC_THRESHOLD is only trusted when there is
        # at least some textual corroboration (match_strength > 0
        # — even a single weak synonym hit). Only similarity at or
        # above STRONG_SEMANTIC_THRESHOLD is trusted on its own,
        # with zero keyword overlap, because at that level CLIP's
        # confidence the content genuinely matches is much higher.
        # This preserves true semantic search (finding a video
        # that matches a description even if no tag/caption word
        # lines up) while cutting off the superficial-similarity
        # false positives.
        # ---------------------------------------------
        STRONG_SEMANTIC_THRESHOLD = 0.33

        results = []

        fallback_candidates = []

        # Videos below this floor are treated as unrelated
        # and never surfaced, even as a fallback.
        MIN_ABS_SIMILARITY = 0.12

        # ---------------------------------------------
        # Search Every Video
        # ---------------------------------------------
        for index, video_embedding in enumerate(self.embeddings):

            # -----------------------------------------
            # Prevent Metadata / Embedding Mismatch
            # -----------------------------------------
            if index >= len(self.metadata):
                continue

            similarity = float(
                np.dot(query_embedding, video_embedding) /
                (
                    np.linalg.norm(query_embedding)
                    * np.linalg.norm(video_embedding)
                    + 1e-10
                )
            )

            # ---------------------------------------------
            # Ignore Clearly Unrelated Videos
            # ---------------------------------------------
            if similarity < MIN_ABS_SIMILARITY:
                continue

            score = similarity * 100

            semantic_match = similarity >= 0.28

            strong_semantic_match = similarity >= STRONG_SEMANTIC_THRESHOLD

            metadata = self.metadata[index]

            filename = metadata["filename"].lower()

            objects = [obj.lower() for obj in metadata.get("objects", [])]

            tags = [tag.lower() for tag in metadata.get("tags", [])]

            caption = metadata.get("caption", "").lower()

            searchable = metadata.get("searchable", "").lower()

            match_count = 0.0

            match_strength = 0.0

            # ---------------------------------------------
            # Keyword + Semantic Boosting (single pass per word)
            # ---------------------------------------------
            for word in query_words:

                is_literal = self.is_word_variant(word, original_words)

                weight = 1.0 if is_literal else SYNONYM_WEIGHT

                # -----------------------------------------
                # Field trust factor
                # -----------------------------------------
                # The reduced factors below (0.75/0.85 for
                # caption/searchable/partial matches) exist to
                # stop a LOOSE SYNONYM from counting as strong
                # evidence just because it shows up in a long
                # free-text sentence. They should NOT discount
                # the user's own literal word — if someone
                # searches "graduation" and "graduation" is
                # genuinely present in the caption or searchable
                # text (very common: real tag lists are often
                # generic/generic-object-only, while the actual
                # descriptive word only lives in the caption
                # sentence), that's a real, trustworthy match on
                # its own and should count at full strength
                # regardless of which field it was found in.
                # -----------------------------------------
                def field_factor(key):
                    return 1.0 if is_literal else FIELD_FACTOR[key]

                # Strongest single field hit for THIS word only.
                word_strength = 0.0

                # -----------------------------------------
                # Filename
                # -----------------------------------------
                if self.word_match(word, filename):
                    score += 60 * weight
                    match_count += weight
                    word_strength = max(
                        word_strength, weight * field_factor("filename")
                    )

                # -----------------------------------------
                # Objects
                # -----------------------------------------
                for obj in objects:

                    if word == obj:
                        score += 100 * weight
                        match_count += weight
                        word_strength = max(
                            word_strength,
                            weight * field_factor("object_exact")
                        )

                    elif self.word_match(word, obj):
                        score += 55 * weight
                        match_count += weight
                        word_strength = max(
                            word_strength,
                            weight * field_factor("object_partial")
                        )

                # -----------------------------------------
                # Tags
                # -----------------------------------------
                for tag in tags:

                    if word == tag:
                        score += 55 * weight
                        match_count += weight
                        word_strength = max(
                            word_strength, weight * field_factor("tag_exact")
                        )

                    elif self.word_match(word, tag):
                        score += 30 * weight
                        match_count += weight
                        word_strength = max(
                            word_strength,
                            weight * field_factor("tag_partial")
                        )

                # -----------------------------------------
                # Caption
                # -----------------------------------------
                if self.word_match(word, caption):
                    score += 35 * weight
                    score += 10 * weight  # semantic bonus
                    word_strength = max(
                        word_strength, weight * field_factor("caption")
                    )

                # -----------------------------------------
                # Searchable Text
                # -----------------------------------------
                if self.word_match(word, searchable):
                    score += 25 * weight
                    score += 8 * weight  # semantic bonus
                    word_strength = max(
                        word_strength, weight * field_factor("searchable")
                    )

                match_strength += word_strength

            # ---------------------------------------------
            # Multiple Match Bonus
            # ---------------------------------------------
            score += match_count * 12

            # ---------------------------------------------
            # Decide Inclusion
            # -----------------------------------------------
            # A video is included when ANY of the following holds:
            #   1. strong_keyword_match — accumulated per-word
            #      match strength clears the threshold (one
            #      strong literal/variant hit, or several
            #      independently-corroborating synonym hits).
            #   2. strong_semantic_match — CLIP is confident enough
            #      on its own (>= STRONG_SEMANTIC_THRESHOLD) that no
            #      textual corroboration is required.
            #   3. semantic_match AND match_strength > 0 — CLIP is
            #      moderately confident AND there's at least some
            #      (even weak) textual corroboration, so it isn't
            #      pure superficial-visual-similarity noise.
            # ---------------------------------------------
            strong_keyword_match = match_strength >= MATCH_STRENGTH_THRESHOLD

            include = (
                strong_keyword_match
                or strong_semantic_match
                or (semantic_match and match_strength > 0)
            )

            # ---------------------------------------------
            # Final Result
            # ---------------------------------------------
            thumbnail_name = Path(metadata["thumbnail"]).name

            candidate = {
                "filename": metadata["filename"],
                "thumbnail": thumbnail_name,
                "duration": metadata.get("duration", ""),
                "objects": metadata.get("objects", []),
                "caption": metadata.get("caption", ""),
                "tags": metadata.get("tags", []),
                "score": round(score, 2),
                "_similarity": similarity
            }

            if include:
                results.append(candidate)

            else:
                # Doesn't clear the normal bar, but isn't
                # unrelated either — kept in case nothing
                # else qualifies (e.g. a video whose content
                # falls outside the known tag/keyword
                # vocabulary entirely).
                fallback_candidates.append(candidate)

        # ---------------------------------------------
        # Fallback: Nothing Passed The Normal Filter
        # ---------------------------------------------
        # Only used when the strict pass found zero results.
        # Critically, this only includes near-misses — videos
        # that came reasonably close to the semantic_match bar
        # (0.28) — not anything down at the noise floor
        # (MIN_ABS_SIMILARITY, 0.12). CLIP similarity between
        # genuinely unrelated content still commonly sits in
        # the 0.12-0.20 range just from general correlation, so
        # falling back that low returns essentially random
        # videos with high confidence, which is worse than
        # returning nothing. FALLBACK_MIN_SIMILARITY is set
        # close to the real match bar so a fallback result only
        # appears when it's a credible near-match, not noise.
        # ---------------------------------------------
        FALLBACK_MIN_SIMILARITY = 0.24

        if not results and fallback_candidates:

            fallback_candidates = [
                item for item in fallback_candidates
                if item["_similarity"] >= FALLBACK_MIN_SIMILARITY
            ]

            fallback_candidates.sort(
                key=lambda x: x["_similarity"], reverse=True
            )

            results = fallback_candidates

        # ---------------------------------------------
        # Sort Results
        # ---------------------------------------------
        results.sort(key=lambda x: x["score"], reverse=True)

        # Strip the internal-only similarity field before returning
        for item in results:
            item.pop("_similarity", None)

        return results[:top_k]


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    engine = VideoSearchEngine()

    while True:

        print("\n--------------------------------")

        query = input("Search Video : ").strip()

        if query.lower() == "exit":
            break

        results = engine.search(query)

        print("\n========================================")
        print("Top Video Matches")
        print("========================================")

        if len(results) == 0:
            print("No matching videos found.")

        else:
            for i, video in enumerate(results, start=1):
                print(f"\n{i}. {video['filename']}")
                print(f"Score      : {video['score']}")
                print(f"Duration   : {video['duration']}")
                print(f"Objects    : {video['objects']}")
                print(f"Caption    : {video['caption']}")
                print("-" * 40)

        print("\n========================================")