from ultralytics import YOLO
import os


class ObjectDetector:

    def __init__(self):

        # Better accuracy than yolov8n
        self.model = YOLO("yolov8s.pt")

    def detect_objects(self, image_path):

        results = self.model.predict(
            source=image_path,
            conf=0.15,          # Lower confidence
            iou=0.45,
            verbose=False
        )

        detected_objects = []
        confidence_scores = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(box.cls.item())

                class_name = self.model.names[class_id]

                confidence = float(box.conf.item())

                if class_name not in detected_objects:

                    detected_objects.append(class_name)

                    confidence_scores.append(round(confidence, 2))

        return {

            "image": os.path.basename(image_path),

            "objects": detected_objects,

            "confidence": confidence_scores

        }


if __name__ == "__main__":

    detector = ObjectDetector()

    result = detector.detect_objects("../uploads/test.jpg")

    print(result)