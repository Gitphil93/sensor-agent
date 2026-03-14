import os
from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


SENSOR_ID = get_env("SENSOR_ID")
VENUE_ID = get_env("VENUE_ID")
API_BASE_URL = get_env("API_BASE_URL", "")
API_TOKEN = get_env("API_TOKEN", "")
ARECORD_DEVICE = get_env("ARECORD_DEVICE", "plughw:1,0")
RECORD_SECONDS = int(get_env("RECORD_SECONDS", "10"))
INTERVAL_SECONDS = int(get_env("INTERVAL_SECONDS", "60"))
OUTPUT_DIR = get_env("OUTPUT_DIR", "recordings")