"""Shared I/O and string utilities for server_v2."""
from __future__ import annotations

import json
import re
import threading
from pathlib import Path
from typing import Any


_file_lock = threading.Lock()


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json_file(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def normalize_email(value: str) -> str:
    return str(value or "").strip().lower()


def valid_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalize_email(value)))


def safe_slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-.]", "_", str(value or "").strip())[:64]


def bool_field(obj: dict, key: str, default: bool = True) -> bool:
    value = obj.get(key)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() not in {"false", "0", "no", "off"}
    return bool(value)
