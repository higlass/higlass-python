from pathlib import Path
from tempfile import TemporaryDirectory
import time
import pytest

from higlass.fuse import fuse


def test_fuse_setup_and_teardown():
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        mount_dir = Path(tmp_dir) / "schemas"
        fuse.start(tmp_dir)
        assert mount_dir.is_mount()
        assert fuse.path("http://www.example.com") == str(
            mount_dir / "http" / "www.example.com.."
        )
        assert fuse.path("https://www.example.com") == str(
            mount_dir / "https" / "www.example.com.."
        )
        assert fuse.path("ftp://example.com") == str(
            mount_dir / "ftp" / "example.com.."
        )
        fuse.stop()
        time.sleep(0.1)
        assert not mount_dir.is_mount()


def test_fuse_setup_twice_with_same_dir_is_noop():
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        mount_dir = Path(tmp_dir) / "schemas"
        fuse.start(tmp_dir)
        assert mount_dir.is_mount()
        fuse.start(tmp_dir)
        assert mount_dir.is_mount()
        fuse.stop()
        time.sleep(0.1)
        assert not mount_dir.is_mount()


def test_fuse_setup_and_teardown_twice_with_different_dir():
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir1, TemporaryDirectory(
        ignore_cleanup_errors=True
    ) as tmp_dir2:
        mount_dir1 = Path(tmp_dir1) / "schemas"
        mount_dir2 = Path(tmp_dir2) / "schemas"
        fuse.start(tmp_dir1)
        assert mount_dir1.is_mount()
        fuse.start(tmp_dir2)
        time.sleep(0.1)
        assert not mount_dir1.is_mount()
        assert mount_dir2.is_mount()
        fuse.stop()
        time.sleep(0.1)
        assert not mount_dir2.is_mount()


def test_unmount_without_setup():
    from higlass.fuse import FuseProcess

    fuse = FuseProcess()
    with pytest.raises(RuntimeError):
        fuse.unmount()


def test_unmount_after_teardown():
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        fuse.start(tmp_dir)
        fuse.stop()
        with pytest.raises(RuntimeError):
            fuse.unmount()


def test_unmount_then_start():
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        mount_dir = Path(tmp_dir) / "schemas"
        fuse.start(tmp_dir)
        assert mount_dir.is_mount()
        fuse.unmount()
        assert not mount_dir.is_mount()
        fuse.start(tmp_dir)
        assert mount_dir.is_mount()
        fuse.stop()
        time.sleep(0.1)
        assert not mount_dir.is_mount()


def test_path_without_setup():
    with pytest.raises(RuntimeError):
        fuse.path("http://www.example.com")


def test_path_after_teardown():
    with TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        fuse.start(tmp_dir)
        fuse.stop()
        with pytest.raises(RuntimeError):
            fuse.path("http://www.example.com")
