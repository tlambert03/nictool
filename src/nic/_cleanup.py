from pathlib import Path
import time
from typing import Iterator, Union


SEC_PER_DAY = 60 * 60 * 24
TIME = time.time()


def iter_old_files(
    directory: Union[str, Path], min_age: int = 30, safe_match: str = "delete"
) -> Iterator[Path]:
    for path in Path(directory).glob("**/*"):
        if path.is_file():
            days_old = path.stat().st_mtime / SEC_PER_DAY
            if days_old > min_age and safe_match not in str(path):
                yield path


def iter_empty_dirs(directory: Union[str, Path]) -> Iterator[Path]:
    for path in Path(directory).glob("**/*"):
        if path.is_dir() and not list(path.iterdir()):
            yield path
