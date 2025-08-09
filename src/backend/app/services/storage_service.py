import os
from datetime import datetime, timezone


class StorageService:
    UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_images")

    @staticmethod
    def store_image(file_bytes: bytes, filename: str, user) -> str:
        """
        Stores an image file for a user.
        Args:
            file_bytes: The image file as bytes.
            filename: The original filename (for extension).
            user: The user object (must have 'id').
        Returns:
            The relative file path to the stored image.
        Raises:
            ValueError: If input is invalid.
            OSError: If file write or directory creation fails.
        """
        if not isinstance(file_bytes, bytes):
            raise ValueError("file_bytes must be bytes.")
        if not filename or not isinstance(filename, str):
            raise ValueError("filename must be a non-empty string.")
        if not hasattr(user, "id"):
            raise ValueError("user must have an 'id' attribute.")

        # Ensure upload directory exists
        try:
            os.makedirs(StorageService.UPLOAD_DIR, exist_ok=True)
        except Exception as e:
            raise OSError(f"Failed to create upload directory: {e}")

        # Generate unique filename: userID_timestamp.ext
        ext = os.path.splitext(filename)[1] or ".img"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        unique_filename = f"{user.id}_{timestamp}{ext}"
        file_path = os.path.join(StorageService.UPLOAD_DIR, unique_filename)

        # Write file to disk
        try:
            with open(file_path, "wb") as out_file:
                out_file.write(file_bytes)
        except Exception as e:
            raise OSError(f"Failed to write image file: {e}")

        # Return relative path
        rel_path = os.path.relpath(file_path, os.getcwd())
        return rel_path

    @staticmethod
    def load_image(user, image_key: str) -> bytes:
        """
        Loads an image file for a user from local storage.
        Args:
            user: The user object (must have 'id').
            image_key: The relative file path or storage key.
        Returns:
            The image file as bytes.
        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the user does not have access to the file.
            OSError: If file read fails.
        """
        # For now, only local storage is supported. In future, add cloud backend logic here.
        if not hasattr(user, "id"):
            raise ValueError("user must have an 'id' attribute.")
        # Security: Ensure image_key is within the upload directory
        abs_path = os.path.abspath(os.path.join(os.getcwd(), image_key))
        if not abs_path.startswith(os.path.abspath(StorageService.UPLOAD_DIR)):
            raise PermissionError("Access to the requested file is denied.")
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Image file not found: {image_key}")
        # (Optional) Check user ownership if file naming convention is enforced
        if not os.path.basename(abs_path).startswith(str(user.id)):
            raise PermissionError("User does not have access to this image.")
        try:
            with open(abs_path, "rb") as f:
                return f.read()
        except Exception as e:
            raise OSError(f"Failed to read image file: {e}")
