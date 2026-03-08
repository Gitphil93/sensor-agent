import logging
import urllib.error
import urllib.request
import json


def check_in(api_base_url: str, api_token: str, sensor_id: str) -> dict:
    url = f"{api_base_url.rstrip('/')}/api/sensor/heartbeat"

    payload = {
        "sensorId": sensor_id,
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