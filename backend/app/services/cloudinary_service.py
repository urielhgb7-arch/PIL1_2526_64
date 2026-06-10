import os
import logging
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

_CLOUDINARY_AVAILABLE = False
_CLOUDINARY_CONFIGURED = False

try:
    import cloudinary
    import cloudinary.uploader
    _CLOUDINARY_AVAILABLE = True
except ImportError:
    logger.info("cloudinary package not installed; avatar uploads will fall back to DB storage.")

def init_cloudinary(app=None):
    global _CLOUDINARY_CONFIGURED
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    api_key = os.environ.get("CLOUDINARY_API_KEY", "")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET", "")

    if all([cloud_name, api_key, api_secret]) and _CLOUDINARY_AVAILABLE:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )
        _CLOUDINARY_CONFIGURED = True
        logger.info("Cloudinary configured successfully.")
    else:
        missing = []
        if not cloud_name: missing.append("CLOUDINARY_CLOUD_NAME")
        if not api_key: missing.append("CLOUDINARY_API_KEY")
        if not api_secret: missing.append("CLOUDINARY_API_SECRET")
        if not _CLOUDINARY_AVAILABLE: missing.append("cloudinary package")
        logger.warning(f"Cloudinary not configured (missing: {', '.join(missing)}). Falling back to DB storage.")

def upload_avatar(file_data, public_id=None):
    """Upload avatar to Cloudinary. Returns URL or None on failure.

    Args:
        file_data: bytes or file-like object of the image.
        public_id: optional public ID (defaults to user ID).

    Returns:
        str — Cloudinary URL, or None if upload failed.
    """
    if not _CLOUDINARY_CONFIGURED:
        logger.warning("Cloudinary not configured, skipping upload.")
        return None

    try:
        if isinstance(file_data, bytes):
            file_data = BytesIO(file_data)

        result = cloudinary.uploader.upload(
            file_data,
            public_id=public_id,
            folder="mentorlink/avatars",
            width=256,
            height=256,
            crop="fill",
            format="jpg",
            quality="auto:best",
        )
        url = result.get("secure_url") or result.get("url")
        logger.info(f"Avatar uploaded to Cloudinary: {url}")
        return url
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}", exc_info=True)
        return None

def delete_avatar(public_id):
    """Delete an avatar from Cloudinary."""
    if not _CLOUDINARY_CONFIGURED:
        return False
    try:
        cloudinary.uploader.destroy(public_id)
        logger.info(f"Avatar deleted from Cloudinary: {public_id}")
        return True
    except Exception as e:
        logger.error(f"Cloudinary delete failed: {e}")
        return False
