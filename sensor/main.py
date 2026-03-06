import logging
import signal
import time

from audio import record_and_process
import settings

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
    logging.info("Loop #%s running for sensor %s", iteration, settings.SENSOR_ID)

    output_file = record_and_process(
        device=settings.ARECORD_DEVICE,
        duration_seconds=settings.RECORD_SECONDS,
        output_dir=settings.OUTPUT_DIR,
    )

    logging.info("New sample created: %s", output_file)


def main():
    global running

    setup_logging()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    iteration = 0

    logging.info("Beatmap sensor starting")
    logging.info("Sensor ID: %s", settings.SENSOR_ID)
    logging.info("Interval: %s seconds", settings.INTERVAL_SECONDS)

    while running:
        iteration += 1

        try:
            tick(iteration)
        except Exception:
            logging.exception("Error in loop iteration")

        if running:
            time.sleep(settings.INTERVAL_SECONDS)

    logging.info("Sensor stopped")


if __name__ == "__main__":
    main()