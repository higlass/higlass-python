from __future__ import annotations

import logging
import multiprocessing as mp
import pathlib
import time
from urllib.parse import urlparse

logger = logging.getLogger("hg.fuse")

__all__ = [
    "FuseProcess",
    "fuse",
]


class FuseProcess:
    _mnt_name = "schemas"
    _dircache_name = "cache"

    def __init__(self):
        self._fuse_process: mp.Process | None = None
        self._tmp_dir: pathlib.Path | None = None

    def start(self, tmp_dir: str | pathlib.Path):
        try:
            from ._httpfs import run
        except ImportError as e:
            raise ImportError(
                'Install "fusepy" and "simple-httpfs" to enable FUSE.'
            ) from e

        # no need to restart
        tmp_dir = pathlib.Path(tmp_dir).absolute()
        if self._fuse_process and tmp_dir == self._tmp_dir:
            logger.debug("Skipping start. FUSE running in same directory %s", tmp_dir)
            return

        self.stop()

        assert tmp_dir.is_dir(), f"mount dir doesn't exist: {tmp_dir}"

        mount_point = tmp_dir / self._mnt_name
        disk_cache_dir = tmp_dir / self._dircache_name

        if not mount_point.exists():
            mount_point.mkdir()

        if not disk_cache_dir.exists():
            disk_cache_dir.mkdir()

        logger.info("Starting FUSE mount at %s", mount_point)

        args = (str(mount_point) + "/", str(disk_cache_dir) + "/")
        self._fuse_process = mp.Process(target=run, args=args, daemon=True)
        self._fuse_process.start()

        max_iters = 10
        for i in range(max_iters):
            # wait until http is mounted
            if (mount_point / "http").exists():
                break

            if i == max_iters - 1:
                self.stop()
                raise RuntimeError("Failed to setup FUSE")

            time.sleep(0.5)

        self._tmp_dir = tmp_dir

    def stop(self):
        if self._fuse_process is None:
            return

        logger.info("Stopping FUSE running at %s", self._tmp_dir)

        self._fuse_process.terminate()
        self._fuse_process = None
        self._tmp_dir = None

        # TODO: remove cache and mount dirs?
        # make sure stuff is no longer mounted

    def path(self, href: str):
        if self._tmp_dir is None:
            raise RuntimeError("FUSE processes not started")
        url = urlparse(href)
        return str(
            self._tmp_dir / self._mnt_name / f"{url.scheme}/{url.netloc}{url.path}.."
        )


fuse = FuseProcess()
