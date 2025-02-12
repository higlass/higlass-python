import warnings

__all__ = ["HiGlassServer"]


class HiGlassServer:
    """Stub for the deprecated `HiGlassServer`.

    `higlass.server` has been removed in favor of Jupyter comms for serving tilesets.
    You no longer need to configure a server manually.

    This class will be removed in a future version.
    """

    def _warn(self):
        warnings.warn(
            "`higlass.server` is deprecated and can be removed from your code. "
            "See: https://github.com/higlass/higlass-python/pull/145 for details.",
            DeprecationWarning,
            stacklevel=3,
        )

    def reset(self):
        self._warn()

    def enable_proxy(self):
        self._warn()

    def disable_proxy(self):
        self._warn()

    def stop(self):
        self._warn()

    def add(self, tileset, port=None):
        raise RuntimeError(
            "`higlass.server` is deprecated. "
            "To add a custom tileset, subclass `hg.Tileset`. "
            "See: https://github.com/higlass/higlass-python/pull/177 for details."
        )
