import re
import cv2
import tempfile
import numpy as np
from pathlib import Path
from collections import Counter

from models.registry import get_clip_model, get_detector, get_blip_model
from utils.tag_generator import generate_tags


class VideoModel:

    def __init__(self):
        print("\n========================================")
        print("Loading Video AI Models...")
        print("========================================")

        # -----------------------------------------
        # AI Models (Shared Across The App)
        # -----------------------------------------
        self.clip = get_clip_model()
        self.detector = get_detector()
        self.blip = get_blip_model()

        print("✓ CLIP Ready")
        print("✓ YOLO Ready")
        print("✓ BLIP Ready")
        print("========================================\n")

    # =====================================================
    # Extract Thumbnail (First Frame)
    # =====================================================
    def extract_thumbnail(self, video_path, thumbnail_path):
        video_path = Path(video_path)
        thumbnail_path = Path(thumbnail_path)

        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise Exception(f"Unable to open video : {video_path}")

        success, frame = cap.read()
        cap.release()

        if not success:
            raise Exception(f"Unable to extract thumbnail : {video_path}")

        cv2.imwrite(str(thumbnail_path), frame)

        return str(thumbnail_path)

    # =====================================================
    # Get Video Duration
    # =====================================================
    def get_duration(self, video_path):
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            return "0 sec"

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()

        if fps <= 0:
            return "0 sec"

        seconds = int(total_frames / fps)
        minutes = seconds // 60
        seconds = seconds % 60

        if minutes > 0:
            return f"{minutes} min {seconds} sec"

        return f"{seconds} sec"

    # =====================================================
    # Resize Frame For Faster Inference
    # =====================================================
    def _resize_frame(self, frame, max_dim=416):
        height, width = frame.shape[:2]

        if max(height, width) <= max_dim:
            return frame

        if width >= height:
            new_width = max_dim
            new_height = int(height * (max_dim / width))
        else:
            new_height = max_dim
            new_width = int(width * (max_dim / height))

        return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # =====================================================
    # Check Frame Quality
    # -----------------------------------------------------
    # Rejects frames that are blurry (low Laplacian variance
    # — a standard focus/sharpness measure), too dark, or
    # blown out (both common on transition/fade frames).
    # Returns (is_valid, sharpness_score) so callers can also
    # rank frames by sharpness when quality alone isn't a
    # hard cutoff.
    # =====================================================
    def _frame_quality(self, frame, blur_threshold=60.0, dark_threshold=25, bright_threshold=230):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

        mean_brightness = gray.mean()

        is_valid = (
            sharpness >= blur_threshold
            and dark_threshold <= mean_brightness <= bright_threshold
        )

        return is_valid, sharpness

    # =====================================================
    # Extract Frames from Entire Video
    # -----------------------------------------------------
    # Samples more candidate positions than actually needed
    # (oversample_factor), then keeps only the sharpest,
    # properly-exposed frames among them — a beach video that
    # happens to have a blurry pan or a dark transition frame
    # at one of the uniformly-sampled positions no longer lets
    # that bad frame dominate the video's embedding/objects.
    # If nothing passes the quality filter (e.g. the whole
    # video is low-contrast), falls back to the raw candidates
    # rather than failing outright.
    # =====================================================
    def extract_frames(self, video_path, sample_count=12, oversample_factor=2):
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise Exception(f"Unable to open video : {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if total_frames <= 0:
            cap.release()
            return []

        # -----------------------------------------
        # Uniform Candidate Sampling (Oversampled)
        # -----------------------------------------
        candidate_count = min(total_frames, sample_count * oversample_factor)

        if total_frames <= candidate_count:
            frame_positions = list(range(total_frames))
        else:
            interval = total_frames / candidate_count
            frame_positions = [int(i * interval) for i in range(candidate_count)]

        raw_frames = []

        for position in frame_positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            success, frame = cap.read()

            if not success:
                continue

            if frame is None:
                continue

            if frame.size == 0:
                continue

            raw_frames.append(frame)

        cap.release()

        # -----------------------------------------
        # Keep The Sharpest, Well-Exposed Frames
        # -----------------------------------------
        scored_frames = []

        for frame in raw_frames:
            is_valid, sharpness = self._frame_quality(frame)

            if is_valid:
                scored_frames.append((sharpness, frame))

        if scored_frames:
            scored_frames.sort(key=lambda item: item[0], reverse=True)
            selected_frames = [frame for _, frame in scored_frames[:sample_count]]

        else:
            # Nothing cleared the quality bar — fall back to the
            # raw candidates so processing can still proceed.
            selected_frames = raw_frames[:sample_count]

        return selected_frames

    # =====================================================
    # Analyze Frames
    # YOLO + BLIP + CLIP
    # -----------------------------------------------------
    # Objects are counted across all frames (not just tracked
    # as present/absent), so something that appears briefly in
    # one frame (e.g. a bus passing in the background) doesn't
    # rank the same as something present throughout the video
    # (e.g. sand, water). Returned objects are ordered by
    # frequency, most common first.
    # =====================================================
    def analyze_frames(self, frames):
        object_counter = Counter()
        captions = []
        frame_embeddings = []

        for frame in frames:
            temp_file = None

            try:
                # -----------------------------------------
                # Save Frame Temporarily
                # -----------------------------------------
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
                    temp_file = Path(temp.name)

                resized_frame = self._resize_frame(frame)

                cv2.imwrite(str(temp_file), resized_frame)

                # -----------------------------------------
                # YOLO Object Detection
                # -----------------------------------------
                detection = self.detector.detect_objects(str(temp_file))

                for obj in detection.get("objects", []):
                    if obj:
                        object_counter[obj.lower()] += 1

                # -----------------------------------------
                # BLIP Caption
                # -----------------------------------------
                caption = self.blip.generate_caption(str(temp_file))

                if caption:
                    caption = caption.strip().lower()
                    if caption != "":
                        captions.append(caption)

                # -----------------------------------------
                # CLIP Image Embedding
                # -----------------------------------------
                try:
                    frame_embedding = self.clip.encode_image(str(temp_file))
                    frame_embeddings.append(frame_embedding)

                except Exception as e:
                    print(f"CLIP embedding warning : {e}")

            except Exception as e:
                print(f"Frame analysis warning : {e}")

            finally:
                if temp_file and temp_file.exists():
                    temp_file.unlink()

        # -----------------------------------------
        # Remove Duplicate Captions
        # -----------------------------------------
        captions = list(dict.fromkeys(captions))

        # -----------------------------------------
        # Order Objects By Frequency (Most Common First)
        # -----------------------------------------
        sorted_objects = [
            obj for obj, _ in
            sorted(object_counter.items(), key=lambda item: (-item[1], item[0]))
        ]

        return sorted_objects, captions, frame_embeddings

    # =====================================================
    # Detect Activities From Captions
    # -----------------------------------------------------
    # YOLO only detects static objects (person, car, ball...)
    # and never actions — CLIP/BLIP look at single frames, not
    # motion across frames — so there is no direct "is this
    # video a dance video" signal in this pipeline. What BLIP
    # captions DO sometimes pick up, per-frame, are action
    # words ("a person dancing", "people walking down a
    # street"). Previously only the single longest caption was
    # kept, so a dance/walking mention in a non-longest caption
    # was diluted into the "searchable" blob as plain text and
    # never became a proper tag your scoring logic boosts on.
    #
    # This scans every frame caption (not just the longest) for
    # a small set of activity keyword families and turns any hit
    # into an explicit tag, using whole-word matching so "dance"
    # doesn't fire on unrelated words. This only makes activity
    # detection as good as BLIP's own captions across the
    # sampled frames — it is not motion analysis or a real
    # action-recognition model, so a dance video BLIP never
    # describes as such still won't be tagged "dancing".
    # =====================================================
    ACTIVITY_KEYWORDS = {
        "dancing": [
            "dance", "dances", "dancing", "dancer", "dancers",
            "choreography"
        ],
        "walking": [
            "walk", "walks", "walking", "walked", "stroll",
            "strolling"
        ],
        "running": [
            "run", "runs", "running", "jogging", "jog"
        ],
    }

    def detect_activities(self, captions):

        if not captions:
            return []

        combined_text = " ".join(captions)

        detected = []

        for activity_tag, keywords in self.ACTIVITY_KEYWORDS.items():

            for keyword in keywords:

                pattern = r"\b" + re.escape(keyword) + r"\b"

                if re.search(pattern, combined_text):
                    detected.append(activity_tag)
                    break

        return detected

    # =====================================================
    # Generate Smart Tags
    # =====================================================
    def build_tags(self, filename, objects):
        tags = generate_tags(filename, objects)

        tags = [tag.lower().strip() for tag in tags if tag.strip()]
        tags = sorted(list(set(tags)))

        return tags

    # =====================================================
    # Build Searchable Text
    # =====================================================
    def build_searchable_text(self, filename, objects, tags, captions):
        searchable = []

        # Filename
        searchable.append(Path(filename).stem.lower())

        # Objects
        searchable.extend(obj.lower() for obj in objects)

        # Tags
        searchable.extend(tag.lower() for tag in tags)

        # Captions
        searchable.extend(caption.lower() for caption in captions)

        # Remove duplicates while preserving order
        searchable = list(dict.fromkeys(searchable))

        return " ".join(searchable)

    # =====================================================
    # Generate CLIP Video Embedding
    # Mean-pooled from per-frame image embeddings
    # =====================================================
    def generate_embedding(self, frame_embeddings):

        if not frame_embeddings:
            raise Exception("No frame embeddings available to build video embedding.")

        stacked = np.stack(frame_embeddings, axis=0)

        embedding = np.mean(stacked, axis=0)

        # Re-normalize after averaging, since the mean of
        # unit vectors is not itself unit length.
        norm = np.linalg.norm(embedding)

        if norm > 0:
            embedding = embedding / norm

        return embedding.astype(np.float32)

    # =====================================================
    # Process Complete Video
    # =====================================================
    def process_video(self, video_path):
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video not found : {video_path}")

        # -----------------------------------------
        # Thumbnail Path
        # -----------------------------------------
        thumbnail_path = (
            video_path.parent.parent
            / "video_frames"
            / f"{video_path.stem}.jpg"
        )

        # -----------------------------------------
        # Generate Thumbnail
        # -----------------------------------------
        self.extract_thumbnail(video_path, thumbnail_path)

        # -----------------------------------------
        # Video Duration
        # -----------------------------------------
        duration = self.get_duration(video_path)

        # -----------------------------------------
        # Extract Frames
        # -----------------------------------------
        # 12 frames (from a 24-candidate oversample) instead of
        # 4 — accuracy matters more than raw processing speed
        # here now that video uploads process in the background
        # (the user isn't waiting on this synchronously anymore).
        # -----------------------------------------
        frames = self.extract_frames(video_path, sample_count=12)

        # -----------------------------------------
        # Empty Video Protection
        # -----------------------------------------
        if len(frames) == 0:
            raise Exception("No frames extracted from video.")

        # -----------------------------------------
        # Analyze Frames
        # -----------------------------------------
        objects, captions, frame_embeddings = self.analyze_frames(frames)

        # -----------------------------------------
        # Smart Tags
        # -----------------------------------------
        tags = self.build_tags(video_path.stem, objects)

        # -----------------------------------------
        # Activity Tags (Dance / Walking / Running)
        # -----------------------------------------
        # Derived from ALL frame captions, not just the single
        # longest one kept below as the display caption — so an
        # activity mentioned in only one or two frames still
        # gets picked up.
        # -----------------------------------------
        activity_tags = self.detect_activities(captions)

        if activity_tags:
            tags = sorted(list(set(tags + activity_tags)))

        # -----------------------------------------
        # Searchable Text
        # -----------------------------------------
        searchable = self.build_searchable_text(
            video_path.stem, objects, tags, captions
        )

        # -----------------------------------------
        # Final Caption
        # -----------------------------------------
        # BLIP rarely produces identical captions across
        # different frames, so a majority vote usually just
        # picks an arbitrary one (most counts are 1). The
        # longest caption is typically the most descriptive.
        # -----------------------------------------
        if len(captions) > 0:
            caption = max(captions, key=len)
        else:
            caption = video_path.stem.replace("_", " ")

        # -----------------------------------------
        # CLIP Embedding (Mean-Pooled Frame Embeddings)
        # -----------------------------------------
        embedding = self.generate_embedding(frame_embeddings)

        # -----------------------------------------
        # Final Output
        # -----------------------------------------
        return {
            "filename": video_path.name,
            "thumbnail": str(thumbnail_path),
            "duration": duration,
            "objects": objects,
            "caption": caption,
            "tags": tags,
            "searchable": searchable,
            "embedding": embedding,
        }


# =====================================================
# Testing
# =====================================================

if __name__ == "__main__":

    model = VideoModel()

    result = model.process_video("../videos/test.mp4")

    print("\n====================================")
    print("Video Processing Completed")
    print("====================================")
    print("Filename   :", result["filename"])
    print("Thumbnail  :", result["thumbnail"])
    print("Duration   :", result["duration"])
    print("Objects    :", result["objects"])
    print("Caption    :", result["caption"])
    print("Tags       :", result["tags"])
    print("Searchable :", result["searchable"])
    print("Embedding Shape :", result["embedding"].shape)
    print("====================================")