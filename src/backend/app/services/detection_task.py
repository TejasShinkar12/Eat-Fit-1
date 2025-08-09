import time
from app.db import SessionLocal
from app.models.image_upload import ImageUpload
from app.models.user import User
from app.models.detection_result import DetectionResult
from app.enums import ImageUploadStatus
from app.services.detection_service import DetectionService
from app.services.storage_service import StorageService
from app.services.ml_services.image_processing.yolo_detector import YOLODetector
from app.utils.logger import get_logger


def run_detection_task(image_upload_id, user_id, file_path):
    logger = get_logger("DetectionTask")
    db = SessionLocal()
    start_time = time.time()
    try:
        # Fetch ImageUpload record
        image_upload = (
            db.query(ImageUpload).filter(ImageUpload.id == image_upload_id).first()
        )
        if not image_upload:
            logger.error(f"ImageUpload not found: {image_upload_id}")
            return
        # Set status to processing
        image_upload.status = ImageUploadStatus.processing
        db.commit()
        logger.info(f"Detection started for image_upload_id={image_upload_id}")

        # Fetch user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User not found: {user_id}")
            image_upload.status = ImageUploadStatus.failed
            image_upload.error_message = f"User not found: {user_id}"
            db.commit()
            return

        # Run detection
        try:
            yolo_detector = YOLODetector()
            detection_service = DetectionService(StorageService, yolo_detector)
            results = detection_service.run_detection(user, file_path)

            new_detections = []
            for result in results:
                new_detection_obj = DetectionResult(
                    image_upload_id=image_upload.id,
                    object_name=result["object_name"],
                    quantity=result["quantity"],
                    confidence=result["confidence"],
                    bbox=result["bbox"],
                    created_at=result["created_at"],
                )
                new_detections.append(new_detection_obj)

            if new_detections:
                db.add_all(new_detections)

            image_upload.detection_results_json = results
            image_upload.status = ImageUploadStatus.complete
            image_upload.error_message = None
            logger.info(
                f"Detection complete for image_upload_id={image_upload_id}, detections={len(results)}"
            )
        except Exception as e:
            image_upload.status = ImageUploadStatus.failed
            image_upload.error_message = str(e)
            logger.error(f"Detection failed for image_upload_id={image_upload_id}: {e}")
        finally:
            db.commit()
    except Exception as e:
        logger.error(f"Detection task error: {e}")
        db.rollback()
    finally:
        db.close()
        duration = time.time() - start_time
        logger.info(
            f"Detection task finished for image_upload_id={image_upload_id} in {duration:.2f}s"
        )
