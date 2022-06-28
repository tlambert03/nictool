import time
from pathlib import Path
from typing import Callable, NamedTuple
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from nic.cli import app
from nic import _cleanup

runner = CliRunner()

NOW = time.time()


class MockStatResult(NamedTuple):
    st_atime: int = 0
    st_ctime: int = 0
    st_dev: int = 0
    st_gid: int = 0
    st_ino: int = 0
    st_mode: int = 0
    st_mtime: int = 0
    st_nlink: int = 0
    st_size: int = 0
    st_uid: int = 0


from os import stat_result
from pathlib import Path

real_stat = Path.stat


@pytest.fixture
def make_data(tmp_path: Path) -> Callable:
    def _make() -> Path:
        for i in range(10):
            (file := tmp_path / f"file_{i}.txt").touch()
            # def _mock_stat():
            #     _stats = list(file.stat())
            #     _stats[8] = NOW + 120 * 24 * 24
            #     _stats[9] = NOW + 120 * 24 * 24
            #     return stat_result(_stats)

            # accs = file._accessor  # type: ignore
            # patch.object(accs, "stat", new_callable=_mock_stat).start()

        return tmp_path

    yield _make


def test_clean(make_data: Callable[..., Path]):
    data_dir = make_data()
    result = runner.invoke(app, ["clean", str(data_dir)])
    assert result.exit_code == 0
    assert "Let's have a coffee in Berlin" in result.stdout
