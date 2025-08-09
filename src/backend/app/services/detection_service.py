import numpy as np
import cv2
from typing import List, Any
from app.services.storage_service import StorageService
from app.services.ml_services.image_processing.yolo_detector import YOLODetector
from app.schemas.detection_result import DetectionResultRead
from app.utils.logger import get_logger
import asyncio


class ImageNotFoundError(Exception):
    pass


class ImageDecodeError(Exception):
    pass


class DetectionError(Exception):
    pass


class DetectionService:
    def __init__(self, storage_service: StorageService, yolo_detector: YOLODetector):
        self.storage = storage_service
        self.detector = yolo_detector
        self.logger = get_logger("DetectionService")
        self.model_version = getattr(yolo_detector, "model_path", "unknown")

    def run_detection(self, user, image_key: str) -> List[DetectionResultRead]:
        """
        Loads an image for the user, decodes it, runs YOLO detection, and returns results.
        Logs detection start, end, duration, and errors.
        """
        import time

        start_time = time.time()
        user_id = getattr(user, "id", None)
        self.logger.info(
            f"Starting detection for user={user_id}, image_key={image_key}"
        )
        try:
            image_bytes = self.storage.load_image(user, image_key)
        except FileNotFoundError:
            self.logger.error(f"Image not found: {image_key} (user={user_id})")
            raise ImageNotFoundError(f"Image not found: {image_key}")
        except PermissionError as e:
            self.logger.error(
                f"Permission error: {e} (user={user_id}, image_key={image_key})"
            )
            raise ImageNotFoundError(str(e))
        except Exception as e:
            self.logger.error(
                f"Failed to load image: {e} (user={user_id}, image_key={image_key})"
            )
            raise ImageNotFoundError(f"Failed to load image: {e}")

        # Decode image bytes to numpy array
        try:
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("cv2.imdecode returned None")
        except Exception as e:
            self.logger.error(
                f"Failed to decode image: {e} (user={user_id}, image_key={image_key})"
            )
            raise ImageDecodeError(f"Failed to decode image: {e}")

        # Run YOLO detection
        try:
            results = self.detector.detect(image)
        except Exception as e:
            self.logger.error(
                f"YOLO detection failed: {e} (user={user_id}, image_key={image_key})"
            )
            raise DetectionError(f"YOLO detection failed: {e}")

        # Map YOLO results to DetectionResultRead schemas (id/image_upload_id/created_at are placeholders)
        import uuid, datetime

        now = datetime.datetime.now(datetime.timezone.utc)
        dummy_image_upload_id = uuid.uuid4()
        detection_schemas = [
            DetectionResultRead(
                id=uuid.uuid4(),
                image_upload_id=dummy_image_upload_id,
                object_name=det["name"],
                quantity=1,  # YOLO doesn't provide quantity, default to 1
                confidence=det["confidence"],
                bbox=det["bbox"],
                created_at=now,
            ).model_dump(mode="json")
            | {"model_version": self.model_version}
            for det in results
        ]
        duration = time.time() - start_time
        self.logger.info(
            f"Detection complete for user={user_id}, image_key={image_key}, duration={duration:.2f}s, detections={len(detection_schemas)}"
        )
        return detection_schemas

    async def async_run_detection(
        self, user, image_key: str
    ) -> list[DetectionResultRead]:
        """
        Async interface for run_detection, suitable for FastAPI BackgroundTasks.
        Runs detection in a thread pool to avoid blocking the event loop.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.run_detection, user, image_key)
