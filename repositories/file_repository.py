import os
import logging
from werkzeug.utils import secure_filename
from datetime import datetime
from exceptions import ValidationError


logger = logging.getLogger(__name__)


class FileRepository:
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    MAX_FILE_SIZE = 16 * 1024 * 1024

    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)

    def save_uploaded_file(self, file) -> str:
        if not file or not file.filename:
            raise ValidationError("No file provided")

        if not self._is_allowed_file(file.filename):
            raise ValidationError(
                f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        filename = self._generate_safe_filename(file.filename)
        file_path = os.path.join(self.upload_folder, filename)

        try:
            file.save(file_path)
        except Exception as e:
            raise ValidationError(f"Failed to save file: {e}")

        return file_path

    def delete_file(self, file_path: str) -> None:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Warning: Failed to delete file {file_path}: {e}")

    def _is_allowed_file(self, filename: str) -> bool:
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )

    def _generate_safe_filename(self, original_filename: str) -> str:
        safe_name = secure_filename(original_filename)
        timestamp = int(datetime.now().timestamp())
        name, ext = os.path.splitext(safe_name)

        return f"{timestamp}_{name}{ext}"
