import logging
import signal
import time

from audio import record_and_process
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
    output_file = record_and_process(
        device="plughw:1,0",
        duration_seconds=10,
        output_dir="recordings",
    )
    logging.info("New sample created: %s", output_file)
    


def main():
    global running

    setup_logging()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    interval_seconds = 60
    iteration = 0

    logging.info("Sensor starting")
    logging.info("Interval: %s seconds", interval_seconds)

    while running:
        iteration += 1

        try:
            tick(iteration)
        except Exception:
            logging.exception("Error in loop")

        if running:
            time.sleep(interval_seconds)

    logging.info("Sensor stopped")


if __name__ == "__main__":
    main()