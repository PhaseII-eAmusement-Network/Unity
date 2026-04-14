from typing import Dict, Any

class UploadData:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024

    @staticmethod
    def update_config(upload_config: Dict[str, Any]) -> None:
        max_content_length = upload_config.get('max_content_length', 64)
        
        UploadData.MAX_CONTENT_LENGTH = max_content_length * 1024 * 1024

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in UploadData.ALLOWED_EXTENSIONS