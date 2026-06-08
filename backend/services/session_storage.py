import os
import re
import shutil
from pathlib import Path

from config import get_settings

PART_PATTERN = re.compile(r"^part_(\d+)(\.[^.]+)?$")


def session_dir(session_id: str) -> str:
    settings = get_settings()
    path = os.path.join(settings.audio_dir, session_id)
    os.makedirs(path, exist_ok=True)
    return path


def part_path(session_id: str, part_index: int, extension: str) -> str:
    ext = extension if extension.startswith(".") else f".{extension}"
    return os.path.join(session_dir(session_id), f"part_{part_index:04d}{ext}")


def save_part(session_id: str, part_index: int, filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower() or ".webm"
    path = part_path(session_id, part_index, ext)
    with open(path, "wb") as f:
        f.write(content)
    return path


def list_part_paths(session_id: str) -> list[tuple[int, str]]:
    directory = session_dir(session_id)
    parts: list[tuple[int, str]] = []

    for name in os.listdir(directory):
        match = PART_PATTERN.match(name)
        if not match:
            continue
        index = int(match.group(1))
        parts.append((index, os.path.join(directory, name)))

    parts.sort(key=lambda item: item[0])
    return parts


def count_parts(session_id: str) -> int:
    return len(list_part_paths(session_id))


def remove_session(session_id: str) -> None:
    directory = os.path.join(get_settings().audio_dir, session_id)
    if os.path.isdir(directory):
        shutil.rmtree(directory, ignore_errors=True)
