"""StorageManager — Multi-Cloud Storage Router
Images  → Cloudinary
Videos  → Firebase Storage
Records → user_files table (SQLite via SQLAlchemy)

All providers are optional: if credentials are missing the service falls
back to local disk storage so the app keeps working without secrets.
"""
from __future__ import annotations
import os, uuid, mimetypes
from pathlib import Path
from typing import Optional

IMAGE_MIMES  = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
VIDEO_MIMES  = {"video/mp4", "video/webm", "video/ogg", "video/quicktime",
                "video/x-msvideo", "video/x-matroska"}

LOCAL_IMAGE_DIR = Path("static/uploads/cloud/images")
LOCAL_VIDEO_DIR = Path("static/uploads/cloud/videos")
LOCAL_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def _detect_type(filename: str, mime: str | None = None) -> str:
    if mime in VIDEO_MIMES:
        return "video"
    if mime in IMAGE_MIMES:
        return "image"
    ext = Path(filename).suffix.lower()
    if ext in {".mp4", ".webm", ".mov", ".avi", ".mkv", ".ogg"}:
        return "video"
    if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
        return "image"
    return "other"


def _cloudinary_configured() -> bool:
    return bool(
        os.environ.get("CLOUDINARY_CLOUD_NAME") and
        os.environ.get("CLOUDINARY_API_KEY") and
        os.environ.get("CLOUDINARY_API_SECRET")
    )


def _firebase_configured() -> bool:
    return bool(
        os.environ.get("FIREBASE_STORAGE_BUCKET") and
        os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    )


def upload_to_cloudinary(file_bytes: bytes, filename: str,
                          folder: str = "ssas") -> dict:
    """Upload an image to Cloudinary. Returns {url, public_id, provider}."""
    import cloudinary, cloudinary.uploader
    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
    )
    import io
    result = cloudinary.uploader.upload(
        io.BytesIO(file_bytes),
        folder=folder,
        resource_type="image",
        public_id=f"{folder}/{uuid.uuid4().hex}",
    )
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "provider": "cloudinary",
    }


def upload_to_firebase(file_bytes: bytes, filename: str,
                        folder: str = "ssas/videos") -> dict:
    """Upload a video to Firebase Storage. Returns {url, public_id, provider}."""
    import json, google.oauth2.service_account as sa
    from google.cloud import storage as gcs
    sa_json = os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"]
    creds = sa.Credentials.from_service_account_info(
        json.loads(sa_json),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = gcs.Client(credentials=creds)
    bucket_name = os.environ["FIREBASE_STORAGE_BUCKET"]
    bucket = client.bucket(bucket_name)
    blob_name = f"{folder}/{uuid.uuid4().hex}_{Path(filename).name}"
    blob = bucket.blob(blob_name)
    mime = mimetypes.guess_type(filename)[0] or "video/mp4"
    blob.upload_from_string(file_bytes, content_type=mime)
    blob.make_public()
    return {
        "url": blob.public_url,
        "public_id": blob_name,
        "provider": "firebase",
    }


def upload_local(file_bytes: bytes, filename: str, file_type: str) -> dict:
    """Fallback: save to local disk. Returns {url, public_id, provider}."""
    safe = f"{uuid.uuid4().hex}_{Path(filename).name}"
    dest_dir = LOCAL_VIDEO_DIR if file_type == "video" else LOCAL_IMAGE_DIR
    dest = dest_dir / safe
    dest.write_bytes(file_bytes)
    relative = str(dest).replace("static/", "/static/", 1)
    return {
        "url": relative,
        "public_id": str(dest),
        "provider": "local",
    }


def route_upload(file_bytes: bytes, filename: str,
                  mime: Optional[str] = None) -> dict:
    """Main router: images → Cloudinary, videos → Firebase, else local.

    Returns:
      {
        "url": str,           # public CDN / storage URL
        "public_id": str,     # provider-side identifier
        "provider": str,      # 'cloudinary' | 'firebase' | 'local'
        "file_type": str,     # 'image' | 'video' | 'other'
        "error": str | None,  # set if the preferred provider failed
      }
    """
    file_type = _detect_type(filename, mime)
    error = None

    if file_type == "image" and _cloudinary_configured():
        try:
            result = upload_to_cloudinary(file_bytes, filename)
            result["file_type"] = "image"
            result["error"] = None
            return result
        except Exception as exc:
            error = f"Cloudinary error: {exc}"

    elif file_type == "video" and _firebase_configured():
        try:
            result = upload_to_firebase(file_bytes, filename)
            result["file_type"] = "video"
            result["error"] = None
            return result
        except Exception as exc:
            error = f"Firebase error: {exc}"

    local = upload_local(file_bytes, filename, file_type)
    local["file_type"] = file_type
    local["error"] = error
    return local


def cloudinary_usage() -> dict:
    """Fetch Cloudinary usage stats. Returns {} if not configured."""
    if not _cloudinary_configured():
        return {}
    try:
        import cloudinary, cloudinary.api
        cloudinary.config(
            cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
            api_key=os.environ["CLOUDINARY_API_KEY"],
            api_secret=os.environ["CLOUDINARY_API_SECRET"],
        )
        data = cloudinary.api.usage()
        return {
            "credits_used": data.get("credits", {}).get("usage", 0),
            "credits_limit": data.get("credits", {}).get("limit", 0),
            "storage_mb": round(data.get("storage", {}).get("usage", 0) / 1e6, 2),
            "transformations": data.get("transformations", {}).get("usage", 0),
            "bandwidth_mb": round(data.get("bandwidth", {}).get("usage", 0) / 1e6, 2),
        }
    except Exception:
        return {}
