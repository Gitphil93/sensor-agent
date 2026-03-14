import logging
import os
import signal
import time

import settings
from audio import record_and_process
from api import check_in, upload_audio

running = True


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def handle_shutdown(signum, frame):
    global running
    logging.info("Got signal %s, shutting down...", signum)
    running = False


def tick(iteration: int) -> int:
    logging.info("Loop #%s running", iteration)

    response = check_in(
        api_base_url=settings.API_BASE_URL,
        api_token=settings.API_TOKEN,
        sensor_id=settings.SENSOR_ID,
        venue_id=settings.VENUE_ID,
    )

    is_active = response.get("isActive", False)
    record_seconds = response.get("recordSeconds", settings.RECORD_SECONDS)
    interval_seconds = response.get("intervalSeconds", settings.INTERVAL_SECONDS)

    logging.info(
        "Check-in success: isActive=%s, recordSeconds=%s, intervalSeconds=%s",
        is_active,
        record_seconds,
        interval_seconds,
    )

    if not is_active:
        logging.info("Sensor is inactive, skipping recording")
        return interval_seconds

    output_file = record_and_process(
        device=settings.ARECORD_DEVICE,
        duration_seconds=record_seconds,
        output_dir=settings.OUTPUT_DIR,
    )

    logging.info("New sample created: %s", output_file)

    upload_result = upload_audio(
        api_base_url=settings.API_BASE_URL,
        api_token=settings.API_TOKEN,
        sensor_id=settings.SENSOR_ID,
        venue_id=settings.VENUE_ID,
        file_path=output_file,
    )

    logging.info("Recognition result: %s", upload_result)

    if output_file and os.path.exists(output_file):
        os.remove(output_file)
        logging.info("Deleted processed file: %s", output_file)

    return interval_seconds


def main():
    global running

    setup_logging()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    iteration = 0

    logging.info("Beatmap sensor starting")
    logging.info("Sensor ID: %s", settings.SENSOR_ID)
    logging.info("Venue ID: %s", settings.VENUE_ID)
    logging.info("Default interval: %s seconds", settings.INTERVAL_SECONDS)

    while running:
        iteration += 1
        sleep_seconds = settings.INTERVAL_SECONDS

        try:
            sleep_seconds = tick(iteration)
        except Exception:
            logging.exception("Error in loop iteration")

        if running:
            time.sleep(max(1, int(sleep_seconds)))

    logging.info("Sensor stopped")


if __name__ == "__main__":
    main()