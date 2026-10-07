import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional

class DatasetCache:
    """Safe dataset memory cache keyed by file path and file modification time (mtime)."""

    _cache: Dict[str, Tuple[float, pd.DataFrame]] = {}

    @classmethod
    def get_dataframe(cls, path: Path | str) -> Optional[pd.DataFrame]:
        p = Path(path).resolve()
        if not p.exists():
            return None

        mtime = p.stat().st_mtime
        key = str(p)

        if key in cls._cache:
            cached_mtime, df = cls._cache[key]
            if cached_mtime == mtime:
                return df.copy()

        df = pd.read_csv(p)
        cls._cache[key] = (mtime, df)
        return df.copy()

    @classmethod
    def clear(cls):
        cls._cache.clear()
