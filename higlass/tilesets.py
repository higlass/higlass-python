import clodius.tiles.bigwig as hgbi
import clodius.tiles.chromsizes as hgch
import clodius.tiles.cooler as hgco
import clodius.tiles.mrmatrix as hgmm

import clodius.tiles.utils as hgut
import clodius.tiles.format as hgfo

import h5py
import slugid 

class Tileset:
    def __init__(self, tileset_info=None, 
            tiles=None, 
            uuid=None,
            chromsizes=lambda: None,
            track_type=None,
            track_position=None):
        '''
        Parameters 
        ----------
        tileset_info: function 
            A function returning the information (min_pos, max_pos, max_width, max_zoom),
            for this tileset.
        tiles: function 
            A function returning tile data for this tileset  
        '''
        self.tileset_info_fn = tileset_info 
        self.tiles_fn = tiles
        self.chromsizes_fn = chromsizes
        self.track_type = track_type
        self.track_position = track_position

        if uuid is not None:
            self.uuid = uuid 
        else:
            self.uuid = slugid.nice().decode('utf-8')

    def tileset_info(self):
        return self.tileset_info_fn()

    def tiles(self, tile_ids ):
        return self.tiles_fn(tile_ids)
    
    def chromsizes(self):
        return self.chromsizes_fn()

def cooler(filepath, uuid=None):
    return Tileset(
            tileset_info=lambda: hgco.tileset_info(filepath),
            tiles=lambda tids: hgco.tiles(filepath, tids),
            uuid=uuid,
            track_type='heatmap',
            track_position='center'
        )

def bigwig(filepath, chromsizes=None, uuid=None):
    return Tileset(
            tileset_info=lambda: hgbi.tileset_info(filepath, chromsizes),
            tiles=lambda tids: hgbi.tiles(filepath, tids, chromsizes=chromsizes),
            uuid=uuid
        )

def chromsizes(filepath, uuid=None):
    return Tileset(
            chromsizes=lambda: hgch.get_tsv_chromsizes(filepath),
            uuid=uuid
        )

def mmatrix(filepath, uuid=None):
    f = h5py.File(filepath, 'r')

    return Tileset(
        tileset_info=lambda: hgmm.tileset_info(f),
        tiles=lambda tile_ids: hgut.tiles_wrapper_2d(tile_ids,
                        lambda z,x,y: hgfo.format_dense_tile(
                            hgmm.tiles(f, z, x, y)))
    )

by_filetype = {
    'cooler': cooler,
    'bigwig': bigwig,
}

