import pandas as pd
import numpy as np
import slugid
import h5py

from clodius.tiles.utils import tiles_wrapper_2d, bundled_tiles_wrapper_2d
from clodius.tiles.format import format_dense_tile


class Tileset:
    """
    Object representing a data tileset.

    Parameters
    ----------
    uuid : str
        Tileset uid
    tileset_info : callable
        A function returning the information (min_pos, max_pos, max_width,
        max_zoom) for this tileset.
    tiles : callable
        A function returning tile data for this tileset.
    datatype : str
        Datatype identifier for the viewer
    name : str, optional
        Name for the tileset. Also used as display name for the track.

    """
    def __init__(self, uuid=None, tileset_info=None, tiles=None,
                 chromsizes=lambda: None, datatype="unspecified", name=None,
                 private=False):
        self.uuid = slugid.nice() if uuid is None else uuid
        self.name = name
        self.tileset_info_fn = tileset_info
        self.tiles_fn = tiles
        self.chromsizes_fn = chromsizes
        self.datatype = datatype
        self.private = private

    def tileset_info(self):
        info = self.tileset_info_fn()
        if self.name is not None:
            info['name'] = self.name
        return info

    def tiles(self, tile_ids):
        return self.tiles_fn(tile_ids)

    @property
    def meta(self):
        return {
            "uuid": self.uuid,
            "datatype": self.datatype,
            "private": self.private,
            "name": self.name,
            # 'coordSystem': "hg19",
            # 'coordSystem2': "hg19",
        }


class ChromSizes(Tileset):
    def __init__(self, chromsizes, **kwargs):
        super().__init__(**kwargs)
        self.chromsizes = chromsizes  # TODO: add validation


def chromsizes(filepath, uuid=None, **kwargs):
    from clodius.tiles.chromsizes import get_tsv_chromsizes

    return ChromSizes(
        uuid=uuid,
        chromsizes=get_tsv_chromsizes(filepath),
        datatype='chromsizes',
        **kwargs)


def cooler(filepath, uuid=None, **kwargs):
    from clodius.tiles.cooler import tileset_info, tiles

    return Tileset(
        uuid=uuid,
        tileset_info=lambda: tileset_info(filepath),
        tiles=lambda tids: tiles(filepath, tids),
        datatype='matrix',
        **kwargs
    )


def bigwig(filepath, uuid=None, chromsizes=None, **kwargs):
    from clodius.tiles.bigwig import tileset_info, tiles

    return Tileset(
        uuid=uuid,
        tileset_info=lambda: tileset_info(filepath, chromsizes),
        tiles=lambda tids: tiles(filepath, tids, chromsizes=chromsizes),
        datatype='vector',
        **kwargs
    )


def mrmatrix(filepath, uuid=None, **kwargs):
    from clodius.tiles.mrmatrix import tileset_info, tiles

    f = h5py.File(filepath, "r")

    return Tileset(
        uuid=uuid,
        tileset_info=lambda: tileset_info(f),
        tiles=lambda tile_ids: tiles_wrapper_2d(
            tile_ids, lambda z, x, y: format_dense_tile(tiles(f, z, x, y))
        ),
        datatype='matrix',
        **kwargs
    )


def nplabels(labels_array, uuid=None, importances=None, **kwargs):
    """1d labels"""
    from clodius.tiles import nplabels
    from clodius.tiles import npvector

    return Tileset(
        uuid=uuid,
        tileset_info=lambda: npvector.tileset_info(labels_array,
            bins_per_dimension=16),
        tiles=lambda tids: nplabels.tiles_wrapper(
            labels_array, tids, importances),
        datatype='linear-labels',
        **kwargs
    )


def h5labels(filename, uuid=None, importances=None, **kwargs):
    f = h5py.File(filename, 'r')
    return nplabels(f['labels'], uuid, importances, **kwargs)


def dfpoints(df, x_col, y_col, uuid=None, **kwargs):
    """
    Generate a tileset that serves 2d labelled points from a pandas
    dataframe.

    Parameters
    ----------
    df: :class:`pandas.DataFrame`
        The dataframe containining the data
    x_col: str
        The name of the column containing the x-coordinates
    y_col: str
        The name of the column containing the y-coordinates
    uuid: str
        The uuid of this tileset

    Returns
    -------
    A tileset capapble of serving tiles from this dataframe.

    """
    from clodius.tiles.points import tileset_info, tiles, format_data

    tsinfo = tileset_info(df, x_col, y_col)
    tiles_fn = lambda z, x, y, width=1, height=1: tiles(
        df, x_col, y_col, tsinfo, z, x, y, width, height)

    return Tileset(
        uuid=uuid,
        tileset_info=lambda: tsinfo,
        tiles=lambda tile_ids: format_data(
            bundled_tiles_wrapper_2d(tile_ids, tiles_fn)),
        datatype='scatter-point',
        **kwargs
    )


by_filetype = {
    "cooler": cooler,
    "bigwig": bigwig,
    "mrmatrix": mrmatrix,
    "h5labels": h5labels
}
