"""tools for NIC@HMS"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("nic")
except PackageNotFoundError:
    __version__ = "uninstalled"
__author__ = "Talley Lambert"
__email__ = "talley.lambert@gmail.com"
