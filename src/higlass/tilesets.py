from __future__ import annotations

import functools
import pathlib
import typing
from dataclasses import dataclass

import higlass.api
from higlass._tileset_registry import TilesetInfo, TilesetProtocol, TilesetRegistry
from higlass._utils import TrackType, datatype_default_track

__all__ = [
    "bed2ddb",
    "bigwig",
    "cooler",
    "hitile",
    "multivec",
    "register",
    "remote",
]

DataType = typing.Literal[
    "2d-rectangle-domains",
    "bedlike",
    "chromsizes",
    "gene-annotations",
    "matrix",
    "multivec",
    "vector",
]

T = typing.TypeVar("T", bound=TilesetProtocol)


def register(klass: type[T]) -> type[T]:
    """Decorator that adds a `track` method to a class implementing `TilesetProtocol`.

    The `track` method automatically registers the tileset with the `TilesetRegistry`
    and returns a HiGlass track object, which can be used for visualization.

    Parameters
    ----------
    klass : type[T]
        A class that implements `TilesetProtocol`.

    Returns
    -------
    type[T]
        The input class, now with an added `track` method.

    Examples
    --------
    >>> from dataclasses import dataclass
    >>> from clodius.tiles.cooler import tiles, tileset_info
    >>>
    >>> @register
    >>> @dataclass
    >>> class MyCoolerTileset:
    >>>     filepath: str
    >>>     datatype = "matrix"
    >>>
    >>>     def info(self):
    >>>         return tileset_info(self.filepath)
    >>>
    >>>     def tiles(self, tile_ids):
    >>>         return tiles(self.filepath, tile_ids)
    >>>
    >>> tileset = MyCoolerTileset("test.mcool")
    >>> track = tileset.track("heatmap")
    """

    def track(
        self: TilesetProtocol, type_: TrackType | None = None, /, **kwargs
    ) -> higlass.api.Track:
        """
        Create a HiGlass track for the tileset.

        Registers the tileset with the `TilesetRegistry` and returns a track
        of the given `type_`. Defaults to a type based on the tileset's `datatype`
        if not specified.

        Parameters
        ----------
        type_ : TrackType, optional
            Track type. If `None`, a default is inferred.

        Returns
        -------
        higlass.api.Track
            The configured HiGlass track.
        """
        # use default track based on datatype if available
        if type_ is None:
            datatype = getattr(self, "datatype", None)
            if datatype is None:
                raise ValueError("No default track for tileset")
            else:
                type_ = typing.cast(TrackType, datatype_default_track[datatype])

        # add tileset registry and get an identifier
        uid = TilesetRegistry.add(self)
        track = higlass.api.track(
            type_=type_,
            server="jupyter",
            tilesetUid=uid,
            **kwargs,
        )
        name = getattr(self, "name", None)
        if name is not None:
            track.opts(name=name, inplace=True)

        return track

    setattr(klass, "track", track)
    return klass


@dataclass
class RemoteTileset:
    uid: str
    server: str
    name: str | None = None

    def track(self, type_: TrackType, **kwargs):
        track = higlass.api.track(
            type_=type_,
            server=self.server,
            tilesetUid=self.uid,
            **kwargs,
        )
        if self.name is not None:
            track.opts(name=self.name, inplace=True)
        return track


def remote(
    uid: str, server: str = "https://higlass.io/api/v1", name: str | None = None
):
    """Create a remote tileset reference.

    Parameters
    ----------
    uid : str
        The unique identifier for the remote tileset.
    server : str, optional
        The HiGlass server URL (default is "https://higlass.io/api/v1").
    name : str, optional
        An optional name for the tileset.

    Returns
    -------
    RemoteTileset
        A RemoteTileset instance that can be used to create HiGlass tracks.
    """
    return RemoteTileset(uid, server, name)


@register
@dataclass
class ClodiusTileset(TilesetProtocol):
    datatype: DataType
    tiles_impl: typing.Callable[[typing.Sequence[str]], list[typing.Any]]
    info_impl: typing.Callable[[], TilesetInfo]

    def tiles(self, *, tile_ids: typing.Sequence[str]) -> list[dict]:
        return self.tiles_impl(tile_ids)

    def info(self) -> TilesetInfo:
        return self.info_impl()


def create_lazy_clodius_loader(
    kind: str, datatype: DataType
) -> typing.Callable[[str | pathlib.Path], ClodiusTileset]:
    def load(filepath: str | pathlib.Path) -> ClodiusTileset:
        try:
            module = __import__(
                f"clodius.tiles.{kind}", fromlist=["tiles", "tileset_info"]
            )
        except (ImportError, AttributeError):
            raise ImportError(f"You must have `clodius` installed to use `hg.{kind}`.")

        return ClodiusTileset(
            datatype=datatype,
            tiles_impl=functools.partial(module.tiles, filepath),
            info_impl=functools.partial(module.tileset_info, filepath),
        )

    return load


bed2ddb = create_lazy_clodius_loader("bed2ddb", datatype="2d-rectangle-domains")
beddb = create_lazy_clodius_loader("beddb", datatype="vector")
bigwig = create_lazy_clodius_loader("bigwig", datatype="vector")
cooler = create_lazy_clodius_loader("cooler", datatype="matrix")
hitile = create_lazy_clodius_loader("hitile", datatype="vector")
multivec = create_lazy_clodius_loader("multivec", datatype="multivec")
