import base64
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

from app.core.config import settings


def _base64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _parse_definition(value: str) -> Optional[Any]:
    if not value:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    if "," in stripped:
        parts = [p.strip() for p in stripped.split(",") if p.strip()]
        values = []
        for part in parts:
            if part.isdigit():
                values.append(int(part))
            else:
                values.append(part)
        return values
    if stripped.isdigit():
        return int(stripped)
    return stripped


def _build_content_info() -> Dict[str, Any]:
    content_info: Dict[str, Any] = {
        "audioVideoType": settings.VOD_PSIGN_AUDIO_VIDEO_TYPE,
    }
    if content_info["audioVideoType"] == "RawAdaptive":
        definition = _parse_definition(settings.VOD_PSIGN_RAW_ADAPTIVE_DEFINITION)
        if definition is not None:
            content_info["rawAdaptiveDefinition"] = definition
    if content_info["audioVideoType"] == "Transcode":
        definition = _parse_definition(settings.VOD_PSIGN_TRANSCODE_DEFINITION)
        if definition is not None:
            content_info["transcodeDefinition"] = definition
    return content_info


def generate_psign(file_id: str, now_ts: Optional[int] = None) -> Dict[str, Any]:
    if settings.VOD_APP_ID == 0 or not settings.VOD_PLAY_KEY:
        raise ValueError("VOD_APP_ID or VOD_PLAY_KEY is not configured")
    if not file_id:
        raise ValueError("file_id is required")

    current_ts = now_ts or int(time.time())
    expire_ts = current_ts + settings.VOD_PSIGN_EXPIRE_SECONDS
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "appId": settings.VOD_APP_ID,
        "fileId": file_id,
        "contentInfo": _build_content_info(),
        "currentTimeStamp": current_ts,
        "expireTimeStamp": expire_ts,
    }

    header_b64 = _base64url_encode(
        json.dumps(header, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    )
    payload_b64 = _base64url_encode(
        json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    )
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(
        settings.VOD_PLAY_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_b64 = _base64url_encode(signature)

    return {
        "psign": f"{header_b64}.{payload_b64}.{signature_b64}",
        "file_id": file_id,
        "app_id": settings.VOD_APP_ID,
        "expire_time": expire_ts,
    }
