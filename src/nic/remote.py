from __future__ import annotations

import os
import subprocess
import tempfile
from contextlib import contextmanager
from getpass import getpass
from typing import Iterator
from urllib.parse import quote


@contextmanager
def mount_smb(
    server: str,
    share: str = "data",
    user: str = "Admin",
    password: str | None = None,
) -> Iterator[str]:
    """Mount smb share at `//server/share` to a temporary directory."""
    password = password or os.getenv("NIC_PASSWORD") or getpass("NIC Password: ")
    if not password:
        raise ValueError("Password required")

    target = f"//{quote(user)}:{quote(password)}@{server}/{quote(share)}"
    mountpoint = tempfile.mkdtemp()
    cmd = ["mount", "-t", "smbfs", target, mountpoint]
    response = subprocess.run(cmd)
    if response.returncode != 0:
        raise RuntimeError("Failed to mount SMB share")
    try:
        yield mountpoint
    finally:
        subprocess.run(["umount", mountpoint])
        os.rmdir(mountpoint)
