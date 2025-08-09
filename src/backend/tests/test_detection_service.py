import pytest
import uuid
import numpy as np
from unittest.mock import Mock
from app.services.detection_service import (
    DetectionService,
    ImageNotFoundError,
    ImageDecodeError,
    DetectionError,
)
from app.schemas.detection_result import DetectionResultRead
import asyncio


class DummyUser:
    def __init__(self, id=None):
        self.id = id or uuid.uuid4()


def test_run_detection_valid(monkeypatch):
    user = DummyUser()
    image_key = "uploaded_images/{}.jpg".format(user.id)
    # Mock storage_service
    storage_service = Mock()
    # Create a valid JPEG image in memory
    import cv2

    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, img_bytes = cv2.imencode(".jpg", img)
    storage_service.load_image.return_value = img_bytes.tobytes()
    # Mock yolo_detector
    yolo_detector = Mock()
    yolo_detector.model_path = "yolov8m.pt"
    yolo_detector.detect.return_value = [
        {"name": "apple", "class_id": 0, "confidence": 0.95, "bbox": [1, 2, 3, 4]},
        {"name": "banana", "class_id": 1, "confidence": 0.85, "bbox": [5, 6, 7, 8]},
    ]
    service = DetectionService(storage_service, yolo_detector)
    results = service.run_detection(user, image_key)
    assert isinstance(results, list)
    assert results[0]["object_name"] == "apple"
    assert results[1]["object_name"] == "banana"
    assert results[0]["model_version"] == "yolov8m.pt"
    assert "id" in results[0]
    assert "created_at" in results[0]


def test_run_detection_file_not_found():
    user = DummyUser()
    storage_service = Mock()
    storage_service.load_image.side_effect = FileNotFoundError()
    yolo_detector = Mock()
    service = DetectionService(storage_service, yolo_detector)
    with pytest.raises(ImageNotFoundError):
        service.run_detection(user, "missing.jpg")


def test_run_detection_decode_error():
    user = DummyUser()
    storage_service = Mock()
    storage_service.load_image.return_value = b"notanimage"
    yolo_detector = Mock()
    service = DetectionService(storage_service, yolo_detector)
    with pytest.raises(ImageDecodeError):
        service.run_detection(user, "bad.jpg")


def test_run_detection_detection_error():
    user = DummyUser()
    # Valid image bytes
    import cv2

    img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, img_bytes = cv2.imencode(".jpg", img)
    storage_service = Mock()
    storage_service.load_image.return_value = img_bytes.tobytes()
    yolo_detector = Mock()
    yolo_detector.detect.side_effect = Exception("YOLO failed")
    service = DetectionService(storage_service, yolo_detector)
    with pytest.raises(DetectionError):
        service.run_detection(user, "fail.jpg")


@pytest.mark.asyncio
def test_async_run_detection_valid():
    user = DummyUser()
    image_key = "uploaded_images/{}.jpg".format(user.id)
    storage_service = Mock()
    import cv2

    img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, img_bytes = cv2.imencode(".jpg", img)
    storage_service.load_image.return_value = img_bytes.tobytes()
    yolo_detector = Mock()
    yolo_detector.model_path = "yolov8m.pt"
    yolo_detector.detect.return_value = [
        {"name": "apple", "class_id": 0, "confidence": 0.95, "bbox": [1, 2, 3, 4]},
    ]
    service = DetectionService(storage_service, yolo_detector)
    results = asyncio.run(service.async_run_detection(user, image_key))
    assert isinstance(results, list)
    assert results[0]["object_name"] == "apple"
    assert results[0]["model_version"] == "yolov8m.pt"


def test_run_detection_empty_result():
    user = DummyUser()
    image_key = "uploaded_images/{}.jpg".format(user.id)
    storage_service = Mock()
    import cv2

    img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, img_bytes = cv2.imencode(".jpg", img)
    storage_service.load_image.return_value = img_bytes.tobytes()
    yolo_detector = Mock()
    yolo_detector.model_path = "yolov8m.pt"
    yolo_detector.detect.return_value = []
    service = DetectionService(storage_service, yolo_detector)
    results = service.run_detection(user, image_key)
    assert results == []


def test_run_detection_invalid_yolo_output():
    user = DummyUser()
    image_key = "uploaded_images/{}.jpg".format(user.id)
    storage_service = Mock()
    import cv2

    img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, img_bytes = cv2.imencode(".jpg", img)
    storage_service.load_image.return_value = img_bytes.tobytes()
    yolo_detector = Mock()
    yolo_detector.model_path = "yolov8m.pt"
    # Missing 'name' key
    yolo_detector.detect.return_value = [
        {"class_id": 0, "confidence": 0.9, "bbox": [1, 2, 3, 4]}
    ]
    service = DetectionService(storage_service, yolo_detector)
    with pytest.raises(KeyError):
        service.run_detection(user, image_key)


def test_run_detection_permission_error():
    user = DummyUser()
    storage_service = Mock()
    storage_service.load_image.side_effect = PermissionError("No access")
    yolo_detector = Mock()
    service = DetectionService(storage_service, yolo_detector)
    with pytest.raises(ImageNotFoundError):
        service.run_detection(user, "forbidden.jpg")


def test_run_detection_user_without_id():
    class NoIdUser:
        pass

    user = NoIdUser()
    storage_service = Mock()
    storage_service.load_image.side_effect = ValueError(
        "user must have an 'id' attribute."
    )
    yolo_detector = Mock()
    service = DetectionService(storage_service, yolo_detector)
    with pytest.raises(ImageNotFoundError):
        service.run_detection(user, "any.jpg")


def test_logging_on_error(monkeypatch):
    user = DummyUser()
    storage_service = Mock()
    storage_service.load_image.side_effect = FileNotFoundError()
    yolo_detector = Mock()
    service = DetectionService(storage_service, yolo_detector)
    logs = []

    class DummyLogger:
        def info(self, msg):
            logs.append(("info", msg))

        def error(self, msg):
            logs.append(("error", msg))

    service.logger = DummyLogger()
    with pytest.raises(ImageNotFoundError):
        service.run_detection(user, "missing.jpg")
    assert any(l[0] == "error" and "Image not found" in l[1] for l in logs)
