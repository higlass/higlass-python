from __future__ import annotations

import atexit
import logging
import multiprocessing as mp
import pathlib
import platform
import subprocess
import time
import warnings
from urllib.parse import urlparse

logger = logging.getLogger("higlass.fuse")

__all__ = [
    "fuse",
    "FuseProcess",
]

OS_NAME = platform.system()


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

        tmp_dir = pathlib.Path(tmp_dir).absolute()
        if not tmp_dir.is_dir():
            raise NotADirectoryError(f"Mount dir doesn't exist: {tmp_dir}")

        mount_point = tmp_dir / self._mnt_name
        disk_cache_dir = tmp_dir / self._dircache_name

        # No need to restart if already running and mounted in same directory
        if self._fuse_process and tmp_dir == self._tmp_dir and mount_point.is_mount():
            logger.debug("Skipping start. FUSE running in same directory %s", tmp_dir)
            return

        self.stop()

        if not mount_point.exists():
            mount_point.mkdir()

        if not disk_cache_dir.exists():
            disk_cache_dir.mkdir()

        if mount_point.is_mount():
            logger.info(f"FUSE already mounted at {mount_point}")

            warnings.warn(
                f"Skipping FUSE mount: {mount_point} already mounted. "
                "If you wish to remount call `fuse.unmount()` and "
                "`fuse.start(...)` again. Call `fuse.start(...)` with "
                "a different `tmp_dir` to mount in a different location."
            )
            self._tmp_dir = tmp_dir
        else:
            logger.info(f"Starting FUSE mount at {mount_point}")

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
            atexit.register(self.stop)

    def stop(self):
        if self._fuse_process is None:
            return

        logger.info("Stopping FUSE running at %s", self._tmp_dir)

        self._fuse_process.terminate()
        self._fuse_process = None
        self._tmp_dir = None

        # TODO: remove cache and mount dirs?
        # make sure stuff is no longer mounted

    @property
    def is_mounted(self):
        if self._tmp_dir is None:
            return False
        return (self._tmp_dir / self._mnt_name).is_mount()

    def unmount(self):
        if self._tmp_dir is None:
            raise RuntimeError("FUSE not started")

        if not self.is_mounted:
            raise RuntimeError("FUSE not mounted")

        mount_point = self._tmp_dir / self._mnt_name

        # Stop the FUSE process if it was started by us
        fuse.stop()

        # FUSE might have been started externally, so we need to unmount it
        # manually
        if mount_point.is_mount():
            if OS_NAME == "Darwin":
                p = subprocess.run(["umount", str(mount_point)], capture_output=True)
                if p.returncode != 0:
                    p = subprocess.run(
                        ["diskutil", "unmount", str(mount_point)], capture_output=True
                    )
            else:
                p = subprocess.run(
                    ["fusermount", "-uz", str(mount_point)], capture_output=True
                )

            if not mount_point.is_mount():
                return

            message = f"Failed to unmount FUSE"
            if p.returncode != 0:
                stdout = p.stdout.decode() if p.stdout else ""
                stderr = p.stderr.decode() if p.stderr else ""
                message += f": {' '.join(p.args)} returned {p.returncode}"
                if stdout or stderr:
                    message += f"\n{stdout}\n{stderr}"
            raise RuntimeError(message)

    def path(self, href: str):
        if self._tmp_dir is None:
            raise RuntimeError("FUSE not started")

        if not self.is_mounted:
            raise RuntimeError("httpfs FUSE filesystem is not mounted")

        url = urlparse(href)
        return str(
            self._tmp_dir / self._mnt_name / f"{url.scheme}/{url.netloc}{url.path}.."
        )


fuse = FuseProcess()
