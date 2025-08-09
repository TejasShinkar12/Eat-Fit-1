import pytest
import os
import cv2
from yolo_detector import YOLODetector

MODEL_PATH = "src/ml_services/image_processing/yolov8m.pt"
IMAGE_PATH = "src/ml_services/image_processing/pancakes.jpg"


@pytest.mark.skipif(
    not os.path.exists(MODEL_PATH),
    reason="YOLOv8 model weights not found. Download yolov8m.pt to run this test.",
)
def test_yolo_detector_on_image_path():
    if not os.path.exists(IMAGE_PATH):
        pytest.skip(
            f"Sample image not found. Place '{IMAGE_PATH}' in the test directory."
        )
    detector = YOLODetector(model_path=MODEL_PATH)
    results = detector.detect(IMAGE_PATH)
    assert isinstance(results, list)
    for det in results:
        assert isinstance(det, dict)
        assert set(["name", "class_id", "confidence", "bbox"]).issubset(det.keys())
        assert isinstance(det["name"], str)
        assert isinstance(det["class_id"], int)
        assert isinstance(det["confidence"], float)
        assert isinstance(det["bbox"], list) and len(det["bbox"]) == 4
        assert all(isinstance(x, (int, float)) for x in det["bbox"])
    print("Detections from file path:", results)


@pytest.mark.skipif(
    not os.path.exists(MODEL_PATH),
    reason="YOLOv8 model weights not found. Download yolov8m.pt to run this test.",
)
def test_yolo_detector_on_numpy_array():
    if not os.path.exists(IMAGE_PATH):
        pytest.skip(
            f"Sample image not found. Place '{IMAGE_PATH}' in the test directory."
        )
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        pytest.skip(f"Failed to load image '{IMAGE_PATH}' as numpy array.")
    detector = YOLODetector(model_path=MODEL_PATH)
    results = detector.detect(img)
    assert isinstance(results, list)
    for det in results:
        assert isinstance(det, dict)
        assert set(["name", "class_id", "confidence", "bbox"]).issubset(det.keys())
        assert isinstance(det["name"], str)
        assert isinstance(det["class_id"], int)
        assert isinstance(det["confidence"], float)
        assert isinstance(det["bbox"], list) and len(det["bbox"]) == 4
        assert all(isinstance(x, (int, float)) for x in det["bbox"])
    print("Detections from numpy array:", results)
