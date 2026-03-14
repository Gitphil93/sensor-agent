import json
import logging
import mimetypes
import os
import urllib.error
import urllib.request
import uuid


def check_in(api_base_url: str, api_token: str, sensor_id: str, venue_id: str) -> dict:
    url = f"{api_base_url.rstrip('/')}/sensor/heartbeat"

    payload = {
        "sensorId": sensor_id,
        "venueId": venue_id,
        "status": "online",
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body)
            logging.info("Check-in success: %s", parsed)
            return parsed

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logging.error("Check-in HTTP error %s: %s", e.code, body)
        raise

    except urllib.error.URLError as e:
        logging.error("Check-in URL error: %s", e)
        raise


def upload_audio(
    api_base_url: str,
    api_token: str,
    sensor_id: str,
    venue_id: str,
    file_path: str,
) -> dict:
    url = f"{api_base_url.rstrip('/')}/sensor/recognize"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    boundary = f"----BeatmapBoundary{uuid.uuid4().hex}"
    file_name = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    parts: list[bytes] = []

    def add_field(name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8")
        )
        parts.append(value.encode("utf-8"))
        parts.append(b"\r\n")

    add_field("sensorId", sensor_id)
    add_field("venueId", venue_id)

    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(
        (
            f'Content-Disposition: form-data; name="audio"; '
            f'filename="{file_name}"\r\n'
        ).encode("utf-8")
    )
    parts.append(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))

    body = b"".join(parts)

    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body)
            logging.info("Upload success: %s", parsed)
            return parsed

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logging.error("Upload HTTP error %s: %s", e.code, body)
        raise

    except urllib.error.URLError as e:
        logging.error("Upload URL error: %s", e)
        raise