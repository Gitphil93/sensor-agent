import logging
import os
import signal
import time

import settings
from audio import record_and_process
from api import check_in


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


def tick(iteration: int):
    logging.info("Loop #%s running", iteration)

    output_file = record_and_process(
        device="plughw:1,0",
        duration_seconds=10,
        output_dir="recordings",
    )
    response = check_in(
    api_base_url=settings.API_BASE_URL,
    api_token=settings.API_TOKEN,
    sensor_id=settings.SENSOR_ID,
    )

    logging.info("New sample created: %s", output_file)

    #Deletes audio file directly while in dev. Todo: delete file after it's processed instead
    if os.path.exists(output_file):
        os.remove(output_file)
        logging.info("Deleted processed file: %s", output_file)


def main():
    global running

    setup_logging()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    interval_seconds = 60
    iteration = 0

    logging.info("Beatmap sensor starting")
    logging.info("Interval: %s seconds", interval_seconds)

    while running:
        iteration += 1

        try:
            tick(iteration)
        except Exception:
            logging.exception("Error in loop iteration")

        if running:
            time.sleep(interval_seconds)

    logging.info("Sensor stopped")


if __name__ == "__main__":
    main()