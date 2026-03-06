import logging
import os
import shutil
import subprocess
from datetime import datetime


def require_command(command_name: str) -> None:
    if shutil.which(command_name) is None:
        raise RuntimeError(
            f"Required command not found: {command_name}. "
            "This script must run on a system where the command is installed."
        )


def run_command(command: list[str]) -> None:
    logging.info("Run command: %s", " ".join(command))
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        logging.error("stdout: %s", result.stdout.strip())
        logging.error("stderr: %s", result.stderr.strip())
        raise RuntimeError(f"Command failed: {' '.join(command)}")


def record_and_process(
    device: str = "plughw:1,0",
    duration_seconds: int = 10,
    output_dir: str = "recordings",
) -> str:
    require_command("arecord")
    require_command("sox")

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    raw_path = os.path.join(output_dir, f"{timestamp}_raw.wav")
    processed_path = os.path.join(output_dir, f"{timestamp}_processed.wav")

    arecord_cmd = [
        "arecord",
        "-D", device,
        "-f", "S32_LE",
        "-r", "48000",
        "-c", "2",
        "-d", str(duration_seconds),
        raw_path,
    ]

    sox_cmd = [
        "sox",
        raw_path,
        processed_path,
        "remix", "1",
        "gain", "-n",
    ]

    logging.info("Recording %s seconds...", duration_seconds)
    run_command(arecord_cmd)

    logging.info("Processing audio to mono + normalized gain...")
    run_command(sox_cmd)

    if os.path.exists(raw_path):
        os.remove(raw_path)
        logging.info("Deleted raw file: %s", raw_path)

    logging.info("Processed file ready: %s", processed_path)
    return processed_path