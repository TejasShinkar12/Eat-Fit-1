from typing import List, Dict
import numpy as np
import os


class YOLODetector:
    """
    YOLOv8 Object Detector using Ultralytics.
    Loads the model once and provides a detect() method for inference.
    """

    def __init__(
        self,
        model_path: str = "C:/Users/TEJAS/Eat-Fit-1/src/backend/app/services/ml_services/image_processing/yolov8m.pt",
    ):
        try:
            from ultralytics import YOLO
        except ImportError:
            raise ImportError(
                "ultralytics package is required. Install with 'pip install ultralytics'."
            )
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model weights not found at {model_path}")
        self.model = YOLO(model_path)

    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        Run YOLOv8 detection on a numpy array image.
        Returns a list of dicts: {name, class_id, confidence, bbox}
        Raises:
            TypeError: if input is not a numpy array
            RuntimeError: if detection fails
        """
        import cv2

        if not isinstance(image, np.ndarray):
            raise TypeError("Input must be a numpy array.")
        try:
            results = self.model(image)
        except Exception as e:
            raise RuntimeError(f"YOLO detection failed: {e}")
        detections = []
        for result in results:
            boxes = result.boxes
            names = result.names
            if len(boxes) == 0:
                continue
            for i in range(len(boxes)):
                class_id = int(boxes.cls[i].item())
                name = names[class_id]
                confidence = float(boxes.conf[i].item())
                bbox = [float(x) for x in boxes.xyxy[i].tolist()]  # [x1, y1, x2, y2]
                detections.append(
                    {
                        "name": name,
                        "class_id": class_id,
                        "confidence": confidence,
                        "bbox": bbox,
                    }
                )
        return detections
