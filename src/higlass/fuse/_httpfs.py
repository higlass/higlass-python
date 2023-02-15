from __future__ import annotations

import logging
from errno import ENOENT

from fuse import FUSE, FuseOSError, LoggingMixIn, Operations
from simple_httpfs import HttpFs
from typing_extensions import Literal

FsName = Literal["http", "https", "ftp"]

logger = logging.getLogger("hg.fuse")


class MultiHttpFs(LoggingMixIn, Operations):
    def __init__(self, schemas: list[FsName], **kwargs):
        logger.info("Starting FUSE at /")
        assert len(schemas) > 0, "must provide at least one schema"
        self.fs = {schema: HttpFs(schema, **kwargs) for schema in schemas}

    def _deref(self, path: str):
        root, *rest = path.lstrip("/").split("/")
        if len(rest) == 1 and rest[0] == "":
            # path == "/http/", "/https/", "/ftp/"
            raise FuseOSError(ENOENT)
        try:
            fs = self.fs[root]
        except KeyError:
            raise FuseOSError(ENOENT)
        return fs, "/" + "/".join(rest)

    def getattr(self, path, fh=None):
        logger.debug("getattr %s", path)
        if path == "/":
            first = next(iter(self.fs.values()))
            return first.getattr("/", fh)
        fs, path = self._deref(path)
        return fs.getattr(path, fh)

    def read(self, path, size, offset, fh):
        logger.debug("read %s", (path, size, offset))
        fs, path = self._deref(path)
        return fs.read(path, size, offset, fh)

    def readdir(self, path, fh):
        logger.debug("readdir %s", path)
        if path[-2:] == "..":
            raise NotADirectoryError(path)
        files = list(self.fs) if path == "/" else []
        return [".", ".."] + files

    def destroy(self, path):
        for fs in self.fs.values():
            fs.destroy(path)


def run(mount_point: str, disk_cache_dir: str):
    fs = MultiHttpFs(
        ["http", "https"],
        disk_cache_size=2**25,
        disk_cache_dir=disk_cache_dir,
        lru_capacity=400,
    )
    FUSE(fs, mount_point, foreground=True)
