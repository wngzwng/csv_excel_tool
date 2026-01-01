from __future__ import annotations

from pathlib import Path
import pandas as pd
from typing import Callable

# ============================================================
# Registry
# ============================================================

_READERS: dict[str, Callable] = {
    ".csv": pd.read_csv,
    ".json": pd.read_json,
    ".xlsx": pd.read_excel,
    ".xls": pd.read_excel,
}

_WRITERS: dict[str, Callable] = {
    ".csv": lambda df, path: df.to_csv(path, index=False),
    ".json": lambda df, path: df.to_json(path, orient="records", lines=True),
    ".xlsx": lambda df, path: df.to_excel(path, index=False),
    ".xls": lambda df, path: df.to_excel(path, index=False),
}

# ============================================================
# Helpers
# ============================================================

def _infer_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    if not suffix:
        raise ValueError(f"Cannot infer file type from path: {path}")
    return suffix


# ============================================================
# Public API (pure path-based)
# ============================================================

def read_df(path: str | Path) -> pd.DataFrame:
    """
    Read DataFrame from a file path.
    """
    path = Path(path)
    suffix = _infer_suffix(path)

    reader = _READERS.get(suffix)
    if not reader:
        raise ValueError(
            f"Unsupported input type: {suffix}. "
            f"Supported: {', '.join(_READERS)}"
        )

    return reader(path)


def write_df(df: pd.DataFrame, path: str | Path) -> None:
    """
    Write DataFrame to a file path.
    """
    path = Path(path)
    suffix = _infer_suffix(path)

    writer = _WRITERS.get(suffix)
    if not writer:
        raise ValueError(
            f"Unsupported output type: {suffix}. "
            f"Supported: {', '.join(_WRITERS)}"
        )

    writer(df, path)
