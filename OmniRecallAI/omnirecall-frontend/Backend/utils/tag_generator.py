# ==========================================================
# Smart Tag Generator
# ==========================================================

import os


def generate_tags(filename, objects):

    filename = filename.lower()

    # Remove extension
    name = os.path.splitext(filename)[0]

    # ---------------------------------------
    # Initial Tags
    # ---------------------------------------

    tags = set()

    # filename words

    for word in name.replace("_", " ").replace("-", " ").split():

        if len(word) > 1:

            tags.add(word)

    # detected objects

    for obj in objects:

        tags.add(obj.lower())

    # ---------------------------------------
    # Scene Dictionary
    # ---------------------------------------

    keyword_map = {

        # ===================================
        # PERSON
        # ===================================

        "person": [
            "person",
            "people",
            "human",
            "man",
            "woman",
            "boy",
            "girl",
            "friends",
            "friend",
            "family",
            "group",
            "team",
            "selfie",
            "portrait",
            "face"
        ],

        # ===================================
        # EDUCATION
        # ===================================

        "college": [
            "college",
            "campus",
            "student",
            "students",
            "education",
            "graduation",
            "class",
            "classroom",
            "friends",
            "school",
            "university"
        ],

        "graduation": [
            "graduation",
            "degree",
            "college",
            "student",
            "education",
            "convocation"
        ],

        # ===================================
        # OFFICE
        # ===================================

        "office": [
            "office",
            "work",
            "meeting",
            "employee",
            "company",
            "business"
        ],

        "laptop": [
            "laptop",
            "computer",
            "coding",
            "developer",
            "software",
            "technology",
            "office",
            "programming"
        ],

        "keyboard": [
            "keyboard",
            "computer",
            "office",
            "typing"
        ],

        "mouse": [
            "mouse",
            "computer",
            "office"
        ],

        # ===================================
        # DOCUMENTS
        # ===================================

        "passport": [
            "passport",
            "travel",
            "id",
            "document"
        ],

        "aadhar": [
            "aadhaar",
            "aadhar",
            "government",
            "identity",
            "document",
            "id"
        ],

        "book": [
            "book",
            "document",
            "study",
            "education"
        ],

        # ===================================
        # FLOWERS
        # ===================================

        "flower": [
            "flower",
            "flowers",
            "rose",
            "garden",
            "nature",
            "plant",
            "green",
            "petals",
            "bloom"
        ],

        "flowers": [
            "flower",
            "flowers",
            "rose",
            "garden",
            "nature",
            "plant"
        ],

        "potted plant": [
            "plant",
            "plants",
            "flower",
            "flowers",
            "garden",
            "nature",
            "green"
        ],

        # ===================================
        # BEACH
        # ===================================

        "beach": [
            "beach",
            "sea",
            "ocean",
            "vacation",
            "holiday",
            "travel",
            "summer"
        ],

        "boat": [
            "boat",
            "river",
            "lake",
            "water",
            "travel"
        ],

        "surfboard": [
            "beach",
            "sea",
            "vacation"
        ],

        # ===================================
        # MOUNTAIN
        # ===================================

        "mountain": [
            "mountain",
            "hill",
            "nature",
            "travel",
            "trekking",
            "forest"
        ],

        # ===================================
        # WEDDING
        # ===================================

        "wedding": [
            "wedding",
            "marriage",
            "bride",
            "groom",
            "ceremony",
            "family",
            "couple"
        ],

        # ===================================
        # BIRTHDAY
        # ===================================

        "cake": [
            "cake",
            "birthday",
            "party",
            "celebration",
            "friends"
        ],

        # ===================================
        # TEMPLE
        # ===================================

        "temple": [
            "temple",
            "god",
            "religion",
            "spiritual",
            "prayer"
        ],

        # ===================================
        # PETS
        # ===================================

        "dog": [
            "dog",
            "puppy",
            "pet",
            "animal"
        ],

        "cat": [
            "cat",
            "kitten",
            "pet",
            "animal"
        ],

        "bird": [
            "bird",
            "birds",
            "parrot",
            "sparrow",
            "nature"
        ],

        # ===================================
        # VEHICLES
        # ===================================

        "car": [
            "car",
            "vehicle",
            "travel",
            "road"
        ],

        "bus": [
            "bus",
            "transport",
            "travel"
        ],

        "train": [
            "train",
            "railway",
            "travel"
        ],

        "airplane": [
            "flight",
            "airport",
            "travel"
        ]
    }

    # ---------------------------------------
    # Filename Rules
    # ---------------------------------------

    filename_rules = {

        "college": [
            "college",
            "campus",
            "students",
            "friends",
            "education"
        ],

        "clg": [
            "college",
            "campus",
            "students",
            "friends"
        ],

        "graduation": [
            "graduation",
            "degree",
            "college",
            "student"
        ],

        "wedding": [
            "wedding",
            "marriage",
            "bride",
            "groom"
        ],

        "birthday": [
            "birthday",
            "cake",
            "party"
        ],

        "beach": [
            "beach",
            "sea",
            "vacation"
        ],

        "mountain": [
            "mountain",
            "nature",
            "travel"
        ],

        "office": [
            "office",
            "meeting",
            "computer"
        ],

        "passport": [
            "passport",
            "document",
            "travel"
        ],

        "aadhar": [
            "aadhaar",
            "document",
            "id"
        ],

        "flower": [
            "flower",
            "flowers",
            "garden",
            "nature"
        ],

        "flowers": [
            "flower",
            "flowers",
            "garden",
            "nature"
        ],

        "friends": [
            "friends",
            "group",
            "people",
            "college"
        ],

        "bird": [
            "bird",
            "birds",
            "nature"
        ],

        "dog": [
            "dog",
            "pet",
            "animal"
        ],

        "cat": [
            "cat",
            "pet",
            "animal"
        ]
    }

    # ---------------------------------------
    # Add object keywords
    # ---------------------------------------

    for obj in objects:

        obj = obj.lower()

        if obj in keyword_map:

            tags.update(keyword_map[obj])

    # ---------------------------------------
    # Add filename keywords
    # ---------------------------------------

    for key in filename_rules:

        if key in filename:

            tags.update(filename_rules[key])

    # ---------------------------------------
    # Searchable sentence keywords
    # ---------------------------------------

    tags.add(name.replace("_", " "))
    tags.add(name.replace("-", " "))

    return sorted(list(tags))