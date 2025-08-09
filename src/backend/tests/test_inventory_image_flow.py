import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.db import SessionLocal
from app.api.deps import get_current_user
import uuid

client = TestClient(app)


# Ensure test user exists in DB and override get_current_user
@pytest.fixture(scope="session", autouse=True)
def override_auth_dependency():
    def _get_test_user():
        # Use a static UUID for consistency
        return User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="testuser@example.com",
            hashed_password="fakehash",
        )

    app.dependency_overrides[get_current_user] = _get_test_user


@pytest.fixture
def test_user(db):
    # Create and return a test user (with static UUID)
    user = (
        db.query(User)
        .filter_by(id=uuid.UUID("11111111-1111-1111-1111-111111111111"))
        .first()
    )
    if not user:
        user = User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="testuser@example.com",
            hashed_password="fakehash",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    yield user
    # Optionally clean up user after tests
    # db.delete(user)
    # db.commit()


def test_upload_image_requires_auth():
    # Remove the override for this test
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    response = client.post(
        "/api/v1/inventory/upload-image",
        files={"file": ("test.jpg", b"fake", "image/jpeg")},
    )
    assert response.status_code == 401

    # Restore the override for other tests
    def _get_test_user():
        return User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="testuser@example.com",
            hashed_password="fakehash",
        )

    app.dependency_overrides[get_current_user] = _get_test_user


def test_upload_image_valid(test_user):
    img_bytes = b"\xff\xd8\xff" + b"0" * 100  # Fake JPEG header
    response = client.post(
        "/api/v1/inventory/upload-image",
        files={"file": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg")},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data and data["status"] == "pending"
    assert data["file_path"].endswith(".jpg")


@pytest.mark.parametrize(
    "filename,content_type",
    [
        ("test.txt", "text/plain"),
        ("test.exe", "application/octet-stream"),
    ],
)
def test_upload_image_invalid_type(test_user, filename, content_type):
    response = client.post(
        "/api/v1/inventory/upload-image",
        files={"file": (filename, b"fake", content_type)},
    )
    assert response.status_code == 400


def create_image_upload_for_user(db, user, status="pending"):
    from app.models.image_upload import ImageUpload
    from app.enums import ImageUploadStatus
    import uuid
    import datetime

    image_upload = ImageUpload(
        id=uuid.uuid4(),
        user_id=user.id,
        file_path=f"uploaded_images/{user.id}_test.jpg",
        status=getattr(ImageUploadStatus, status),
        error_message=None,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(image_upload)
    db.commit()
    db.refresh(image_upload)
    return image_upload


def test_polling_requires_auth():
    # Remove the override for this test
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    import uuid

    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/inventory/image-status/{fake_id}")
    assert response.status_code == 401

    # Restore the override for other tests
    def _get_test_user():
        return User(
            id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
            email="testuser@example.com",
            hashed_password="fakehash",
        )

    app.dependency_overrides[get_current_user] = _get_test_user


def test_polling_not_found(test_user):
    import uuid

    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/inventory/image-status/{fake_id}")
    assert response.status_code == 404


def test_polling_not_owner(test_user, db):
    # Create a second user and an image upload for them
    user2 = User(email="other@example.com", hashed_password="fakehash2")
    db.add(user2)
    db.commit()
    db.refresh(user2)
    image_upload = create_image_upload_for_user(db, user2)
    headers = {"Authorization": f"Bearer fake-token-for-{test_user.email}"}
    response = client.get(
        f"/api/v1/inventory/image-status/{image_upload.id}", headers=headers
    )
    assert response.status_code == 403
    db.delete(image_upload)
    db.delete(user2)
    db.commit()


def test_polling_success(test_user, db):
    image_upload = create_image_upload_for_user(db, test_user, status="pending")
    headers = {"Authorization": f"Bearer fake-token-for-{test_user.email}"}
    response = client.get(
        f"/api/v1/inventory/image-status/{image_upload.id}", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(image_upload.id)
    assert data["status"] == "pending"
    assert data["file_path"] == image_upload.file_path
    db.delete(image_upload)
    db.commit()


def test_full_end_to_end_flow(test_user, db):
    import uuid
    import time
    from app.models.image_upload import ImageUpload
    from app.enums import ImageUploadStatus
    from app.models.inventory import Inventory
    from datetime import date, timedelta

    # 1. Upload image
    img_bytes = b"\xff\xd8\xff" + b"0" * 100
    upload_resp = client.post(
        "/api/v1/inventory/upload-image",
        files={"file": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg")},
    )
    assert upload_resp.status_code == 201
    upload_data = upload_resp.json()
    image_id = upload_data["id"]

    # 2. Simulate detection completion (in real test, poll until status is 'complete')
    image_upload = (
        db.query(ImageUpload).filter(ImageUpload.id == uuid.UUID(image_id)).first()
    )
    image_upload.status = ImageUploadStatus.complete
    image_upload.detection_results_json = [
        {
            "object_name": "apple",
            "quantity": 1,
            "confidence": 0.95,
            "bbox": [1, 2, 3, 4],
        }
    ]
    db.commit()
    db.refresh(image_upload)

    # 3. Poll for status
    poll_resp = client.get(f"/api/v1/inventory/image-status/{image_id}")
    assert poll_resp.status_code == 200
    poll_data = poll_resp.json()
    assert poll_data["status"] == "complete"
    assert poll_data["detection_results_json"][0]["object_name"] == "apple"

    # 4. Review detections
    review_payload = {
        "reviewed_results": [
            {
                "object_name": "apple",
                "quantity": 2,
                "confidence": 0.95,
                "bbox": [1, 2, 3, 4],
            }
        ]
    }
    review_resp = client.post(
        f"/api/v1/inventory/review-detections/{image_id}",
        json=review_payload,
    )
    assert review_resp.status_code == 200
    review_data = review_resp.json()
    assert review_data["reviewed_results"][0]["quantity"] == 2

    # 5. Create inventory from detections
    future_date = (date.today() + timedelta(days=365)).isoformat()
    inventory_payload = {
        "items": [
            {
                "name": "Apple",
                "quantity": 2.0,
                "calories_per_serving": 52.0,
                "protein_g_per_serving": 0.3,
                "carbs_g_per_serving": 14.0,
                "fats_g_per_serving": 0.2,
                "serving_size_unit": "g",
                "expiry_date": future_date,
                "source": "image",
            }
        ]
    }
    create_resp = client.post(
        f"/api/v1/inventory/create-from-detections/{image_id}",
        json=inventory_payload,
    )
    print("Create inventory response:", create_resp.status_code, create_resp.text)
    assert create_resp.status_code == 200
    items = create_resp.json()
    assert isinstance(items, list) and items[0]["name"] == "Apple"

    # Cleanup: delete created inventory and image_upload
    for item in items:
        db_item = (
            db.query(Inventory).filter(Inventory.id == uuid.UUID(item["id"])).first()
        )
        if db_item:
            db.delete(db_item)
    db.delete(image_upload)
    db.commit()


# TODO: Add tests for polling endpoint, review endpoint, inventory creation endpoint, and full flow


def test_review_404(test_user):
    import uuid

    fake_id = uuid.uuid4()
    review_payload = {
        "reviewed_results": [
            {
                "object_name": "apple",
                "quantity": 1,
                "confidence": 0.9,
                "bbox": [1, 2, 3, 4],
            }
        ]
    }
    response = client.post(
        f"/api/v1/inventory/review-detections/{fake_id}", json=review_payload
    )
    assert response.status_code == 404


def test_review_403(test_user, db):
    # Create a second user and an image upload for them
    user2 = User(email="other2@example.com", hashed_password="fakehash2")
    db.add(user2)
    db.commit()
    db.refresh(user2)
    image_upload = create_image_upload_for_user(db, user2)
    headers = {"Authorization": f"Bearer fake-token-for-{test_user.email}"}
    review_payload = {
        "reviewed_results": [
            {
                "object_name": "apple",
                "quantity": 1,
                "confidence": 0.9,
                "bbox": [1, 2, 3, 4],
            }
        ]
    }
    response = client.post(
        f"/api/v1/inventory/review-detections/{image_upload.id}",
        headers=headers,
        json=review_payload,
    )
    assert response.status_code == 403
    db.delete(image_upload)
    db.delete(user2)
    db.commit()


def test_review_422(test_user, db):
    image_upload = create_image_upload_for_user(db, test_user)
    # Invalid payload: missing required fields
    review_payload = {"reviewed_results": [{"object_name": "apple"}]}
    response = client.post(f"/api/v1/inventory/review-detections/{image_upload.id}")
    assert response.status_code == 422
    db.delete(image_upload)
    db.commit()


def test_create_inventory_404(test_user):
    import uuid

    fake_id = uuid.uuid4()
    payload = {
        "items": [
            {
                "name": "Apple",
                "quantity": 1,
                "calories_per_serving": 52,
                "protein_g_per_serving": 0.3,
                "carbs_g_per_serving": 14,
                "fats_g_per_serving": 0.2,
                "serving_size_unit": "g",
                "expiry_date": "2099-12-31",
                "source": "image",
            }
        ]
    }
    response = client.post(
        f"/api/v1/inventory/create-from-detections/{fake_id}", json=payload
    )
    assert response.status_code == 404


def test_create_inventory_403(test_user, db):
    user2 = User(email="other3@example.com", hashed_password="fakehash3")
    db.add(user2)
    db.commit()
    db.refresh(user2)
    image_upload = create_image_upload_for_user(db, user2)
    headers = {"Authorization": f"Bearer fake-token-for-{test_user.email}"}
    payload = {
        "items": [
            {
                "name": "Apple",
                "quantity": 1,
                "calories_per_serving": 52,
                "protein_g_per_serving": 0.3,
                "carbs_g_per_serving": 14,
                "fats_g_per_serving": 0.2,
                "serving_size_unit": "g",
                "expiry_date": "2099-12-31",
                "source": "image",
            }
        ]
    }
    response = client.post(
        f"/api/v1/inventory/create-from-detections/{image_upload.id}",
        headers=headers,
        json=payload,
    )
    assert response.status_code == 403
    db.delete(image_upload)
    db.delete(user2)
    db.commit()


def test_create_inventory_422(test_user, db):
    image_upload = create_image_upload_for_user(db, test_user)
    # Invalid payload: missing required fields
    payload = {"items": [{"name": "Apple"}]}
    response = client.post(
        f"/api/v1/inventory/create-from-detections/{image_upload.id}"
    )
    assert response.status_code == 422
    db.delete(image_upload)
    db.commit()
