import contextlib
import sys

from nic._backup import backup_folders, connect_to_smb
from nic._cleanup import delete_emptydir, delete_old_files
from nic._util import find_userd


def main(noinput: bool = True, age: int = 30, dry: bool = False) -> None:
    try:
        conn = None if noinput else connect_to_smb()
    except Exception as e:
        print(f"Could not make connection: {e}")
    else:
        if not dry:
            backup_folders(conn)

    if userd := find_userd(noinput):
        print(f"\nFound User directory: {userd}")
        print(f"\nDeleting files older than {age} days...")
        print(f"{delete_old_files(userd, age, dry)} Files deleted")
        print("\nDeleting empty directories...")
        print(f"{delete_emptydir(userd, dry)} Directories deleted")


if __name__ == "__main__":
    noinput = False
    try:
        if len(sys.argv) > 1:
            with contextlib.suppress(Exception):
                noinput = bool(int(sys.argv[1]))
        main(noinput)
    except Exception as e:
        print(e)
