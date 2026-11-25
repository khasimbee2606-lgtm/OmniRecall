# ==========================================================
# Shared Model Registry
# ==========================================================
#
# CLIP, YOLO, and BLIP are heavy models (BLIP alone is close
# to a gigabyte). Without this registry, every class that
# needs one of them (VideoModel, PDFModel, SearchEngine,
# VideoSearchEngine, PDFSearchEngine, UploadProcessor) was
# instantiating its own separate copy — meaning a single run
# of app.py could load CLIP six separate times, YOLO twice,
# and BLIP twice.
#
# This module loads each model at most once per process and
# hands back the same shared instance to everyone who asks
# for it. Python only executes a module's top-level code the
# first time it's imported (subsequent imports reuse the
# cached module object), so these globals behave as true
# process-wide singletons regardless of which file imports
# this module first.
# ==========================================================

import os

# -----------------------------------------------------------
# Force Hugging Face Offline Mode
# -----------------------------------------------------------
# transformers' from_pretrained() checks huggingface.co for
# updates even when the model is already cached locally,
# unless told not to. Without internet, that check hangs/fails
# with a DNS error instead of just using the cache — which is
# exactly what happened with BLIP. These must be set before
# transformers (imported via blip_model below) does any actual
# network-touching work, so they're set here, first, before
# that import.
#
# HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE together cover both the
# newer huggingface_hub-based download path and the older
# transformers-internal one, since which one a given
# transformers version uses can vary.
#
# This only works if the model has already been fully
# downloaded and cached at least once with internet access —
# offline mode makes it read from that cache instead of
# checking the network, it can't produce a model that was
# never downloaded in the first place.
# -----------------------------------------------------------
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from models.clip_model import CLIPModel
from models.detector import ObjectDetector
from models.blip_model import BLIPModel

_clip_model = None
_detector = None
_blip_model = None


def get_clip_model():
    global _clip_model

    if _clip_model is None:
        print("✓ Loading shared CLIP model...")
        _clip_model = CLIPModel()

    return _clip_model


def get_detector():
    global _detector

    if _detector is None:
        print("✓ Loading shared YOLO detector...")
        _detector = ObjectDetector()

    return _detector


def get_blip_model():
    global _blip_model

    if _blip_model is None:
        print("✓ Loading shared BLIP model...")
        _blip_model = BLIPModel()

    return _blip_model