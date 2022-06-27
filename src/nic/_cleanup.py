import os
import time


SAFE_WORD = "delete"  # if this word is in the filename, it won't be deleted


def file_age_in_days(file: str) -> float:
    return (time.time() - os.path.getmtime(file)) / (24 * 60 * 60)


def delete_old_files(
    directory: str, age: int = 30, dry: bool = False, safe: str = SAFE_WORD
) -> int:
    deleted = 0
    for root, _, files in os.walk(directory):
        for F in files:
            _f = os.path.join(root, F)
            if file_age_in_days(_f) > age and safe not in _f.lower():
                print(f'{"NOT " if dry else ""}deleting: {_f}')
                if not dry:
                    try:
                        os.remove(_f)
                        deleted += 1
                    except Exception:
                        print(f"ERROR: could not delete file {_f}")

    return deleted


def delete_emptydir(userd: str, dry: bool = False) -> int:
    # delete all empty directories
    totdeleted = 0
    _before = 1
    while _before != totdeleted:
        _before = totdeleted
        for root, _, _ in os.walk(userd):
            if not os.listdir(root):
                print(f"{'NOT ' if dry else ''}deleting: {root}")
                if not dry:
                    try:
                        os.rmdir(root)
                        totdeleted += 1
                    except Exception:
                        print(f"ERROR: could not delete folder {root}")
    return totdeleted
