"""Command line tools for NIC@HMS."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("nic")
except PackageNotFoundError:
    __version__ = "uninstalled"

from ._cleanup import iter_empty_dirs, iter_old_files

__all__ = [
    "iter_old_files",
    "iter_empty_dirs",
]
