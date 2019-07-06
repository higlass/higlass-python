import warnings
import json
import slugid
import sys


__all__ = ['Track', 'CombinedTrack', 'View', 'ViewConf']


_track_default_position = {
    '2d-rectangle-domains': 'center',
    'bedlike': 'top',
    'horizontal-bar': 'top',
    'horizontal-chromosome-labels': 'top',
    'horizontal-gene-annotations': 'top',
    'horizontal-heatmap': 'top',
    'horizontal-1d-heatmap': 'top',
    'horizontal-line': 'top',
    'horizontal-multivec': 'top',
    'heatmap': 'center',
    'left-axis': 'left',
    'osm-tiles': 'center',
    'top-axis': 'top',
    'viewport-projection-center': 'center',
}


_datatype_default_track = {
    '2d-rectangle-domains': '2d-rectangle-domains',
    'bedlike': 'bedlike',
    'chromsizes': 'horizontal-chromosome-labels',
    'gene-annotations': 'horizontal-gene-annotations',
    'matrix': 'heatmap',
    'vector': 'horizontal-bar',
}


class Component:
    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, conf):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError


class Track(Component):
    """
    Configure a Track

    Parameters
    ----------
    track_type : str
        The type of track (e.g. 'heatmap', 'line')
    tileset : uuid or :class:`Tileset`
        The of uuid of the tileset being displayed in this track
    file_url: str
        An http accessible tileset file
    filetype : str
        The type of the remote tilesets (e.g. 'bigwig' or 'cooler')
    server : str, optional
        The server name (usually just 'localhost')
    height : int, optional
        The height of the track (in pixels)
    width : int, optional
        The width of the track (in pixels)
    options : dict, optional
        The options to pass onto the track

    """
    def __init__(self, track_type=None, position=None, tileset=None,
                 file_url=None, filetype=None, **kwargs):
        if track_type is None:
            if 'type' in kwargs:
                track_type = kwargs.pop('type')
            else:
                raise ValueError('Track type is required.')

        self.position = position
        self.tileset = tileset

        # populate the actual config
        self.conf = {"type": track_type, "options": {}}
        if tileset is not None:
            if isinstance(tileset, str):
                self.conf["tilesetUid"] = tileset
            else:
                self.conf["tilesetUid"] = tileset.uuid
        elif 'tileset_uuid' in kwargs:
            self.conf['tilesetUid'] = kwargs.pop('tileset_uuid')
        elif file_url is not None and filetype is not None:
            self.conf["fileUrl"] = file_url
            self.conf["filetype"] = filetype

        self.conf.update(kwargs)

    def change_attributes(self, **kwargs):
        '''
        Change an attribute of this track and return a new copy.
        '''
        conf = self.conf.copy()
        conf.update(kwargs)
        return self.__class__(conf['type'],
                              position=self.position,
                              tileset=self.tileset,
                              **conf)

    def change_options(self, **kwargs):
        '''
        Change one of the track's options in the viewconf
        '''
        new_options = self.conf['options'].copy()
        new_options.update(kwargs)
        return self.change_attributes(options=new_options)

    @classmethod
    def from_dict(cls, conf):
        return cls(**conf)

    def to_dict(self):
        return self.conf.copy()


class CombinedTrack(Track):
    def __init__(self, tracks, position=None, height=100, **kwargs):
        '''
        The combined track contains multiple actual tracks as layers.

        Parameters
        ----------
        tracks: list
            A list of Tracks to add
        '''
        self.tracks = tracks
        self.tileset = None

        # try to get the position from a subtrack
        self.position = position
        if position is None:
            for track in tracks:
                if track.position:
                    self.position = track.position
                    break

        self.height = height
        self.conf = {
            'type': 'combined',
            'height': height,
            'contents': [t.to_dict() for t in self.tracks]
        }

    @classmethod
    def from_dict(cls, conf):
        if 'contents' in conf:
            tracks = [Track.from_dict(track_conf)
                      for track_conf in conf.copy().pop('contents')]
        else:
            tracks = []
        return cls(tracks, **conf)



class View(Component):
    """
    Configure a View

    Parameters
    ----------
    tracks: []
        A list of Tracks to include in this view
    x: int
        The position of this view on the grid
    y: int
        The position of this view on the grid
    width: int
        The width of this of view on a 12 unit grid
    height: int
        The height of the this view. The height is proportional
        to the height of all the views present.
    initialXDoamin: [int, int]
        The initial x range of the view
    initialYDomain: [int, int]
        The initial y range of the view
    uid: string
        The uid of new view

    """
    def __init__(self, tracks=[], x=0, y=0, width=12, height=6,
                 initialXDomain=None, initialYDomain=None, uid=None):
        if uid is None:
            uid = slugid.nice()
        self.uid = uid

        self.conf = {
            "uid": uid,
            "tracks": {"top": [], "center": [], "left": [],
                       "right": [], "bottom": []},
            "layout": {"w": width, "h": height, "x": x, "y": y},
        }
        if initialXDomain is not None:
            self.conf["initialXDomain"] = initialXDomain
        if initialYDomain is not None:
            self.conf["initialYDomain"] = initialYDomain

        self._track_position = {}
        for track in tracks:
            self.add_track(track)

    @property
    def tracks(self):
        return list(self._track_position.keys())

    def add_track(self, track, position=None):
        """
        Add a track to a position.

        Parameters
        ----------
        track_type: string
            The type of track to add (e.g. "heatmap", "line")
        position : {'top', 'bottom', 'center', 'left', 'right'}
            Location for the track within the view
        tileset: hgflask.tilesets.Tileset
            The tileset to be plotted in this track
        server: string
            The server serving this track
        height: int
            The height of the track, if it is a top, bottom or a center track
        width: int
            The width of the track, if it is a left, right or a center track
        """
        track_type = track.conf['type']
        if position is None:
            if track.position is not None:
                position = track.position
            elif track_type in _track_default_position:
                position = _track_default_position[track_type]
            else:
                raise ValueError('Track position is required.')
        self._track_position[track] = position

    @classmethod
    def from_dict(cls, conf):
        layout = conf.get('layout', {})
        self = cls(
            x=layout.get('x', 0),
            y=layout.get('y', 0),
            width=layout.get('w', 12),
            height=layout.get('h', 6),
            initialXDomain=conf.get('initialXDomain', None),
            initialYDomain=conf.get('initialYDomain', None),
            uid=conf.get('uid', None),
        )
        for position in conf.get('tracks', {}):
            for track_conf in conf['tracks'][position]:
                self.add_track(
                    track=Track.from_dict(track_conf),
                    position=position)
        return self

    def to_dict(self):
        """
        Convert the existing track to a JSON representation.
        """
        conf = json.loads(json.dumps(self.conf))
        for track, position in self._track_position.items():
            conf["tracks"][position].append(track.to_dict())
        return conf


class ViewConf(Component):
    """Configure a dashboard"""

    def __init__(self, views=[], location_syncs=[], zoom_syncs=[]):

        self.conf = {
            "editable": True,
            "views": [],
            "trackSourceServers": ["http://higlass.io/api/v1"],
            "locationLocks": {"locksByViewUid": {}, "locksDict": {}},
            "zoomLocks": {"locksByViewUid": {}, "locksDict": {}},
            "exportViewUrl": "http://higlass.io/api/v1/viewconfs",
        }

        self.views = {}
        for view in views:
            self.add_view(view)

        for location_sync in location_syncs:
            self.add_location_sync(location_sync)

        for zoom_sync in zoom_syncs:
            self.add_zoom_sync(zoom_sync)

    def _add_sync(self, lock_group, lock_id, view_uids):
        for view_uid in view_uids:
            if lock_id not in self.conf[lock_group]['locksDict']:
                self.conf[lock_group]['locksDict'][lock_id] = {}
            self.conf[lock_group]["locksDict"][lock_id][view_uid] = (1, 1, 1)
            self.conf[lock_group]["locksByViewUid"][view_uid] = lock_id

    def add_zoom_sync(self, views_to_sync):
        lock_id = slugid.nice()
        # TODO: check that view already exists in viewconf
        self._add_sync("zoomLocks", lock_id, [v.uid for v in views_to_sync])

    def add_location_sync(self, views_to_sync):
        lock_id = slugid.nice()
        # TODO: check that view already exists in viewconf
        self._add_sync("locationLocks", lock_id, [v.uid for v in views_to_sync])

    def add_view(self, view):
        """
        Add a new view

        Parameters
        ----------
        uid: string
            The uid of new view
        width: int
            The width of this of view on a 12 unit grid
        height: int
            The height of the this view. The height is proportional
            to the height of all the views present.
        x: int
            The position of this view on the grid
        y: int
            The position of this view on the grid
        initialXDoamin: [int, int]
            The initial x range of the view
        initialYDomain: [int, int]
            The initial y range of the view

        """
        for uid in self.views.keys():
            if uid == view.uid:
                raise ValueError("View with this uid already exists")
        self.views[view.uid] = view
        return view

    @classmethod
    def from_dict(cls, dct):
        self = cls()

        for view_dct in dct.get('views', []):
            self.add_view(View.from_dict(view_dct))

        locks = dct.get('locationLocks', {}).get('locksDict', {})
        for lock_id, attrs in locks.items():
            self._add_sync('locationLocks', lock_id, attrs.keys())

        locks = dct.get('zoomLocks', {}).get('locksDict', {})
        for lock, attrs in locks.items():
            self._add_sync('zoomLocks', lock_id, attrs.keys())

        return self

    def to_dict(self):
        conf = json.loads(json.dumps(self.conf))
        for view in self.views.values():
            conf["views"].append(view.to_dict())
        return conf


def datatype_to_tracktype(datatype):
    '''
    Infer a default track type from a data type. There can
    be other track types that can display a given data type.

    Parameters
    ----------
    datatype: str
        A datatype identifier (e.g. 'matrix')

    Returns
    -------
    str, str:
        A track type (e.g. 'heatmap') and position (e.g. 'top')

    '''
    track_type = _datatype_default_track.get(datatype, None)
    position = _track_default_position.get(track_type, None)
    return track_type, position
