import json
import slugid
import sys


track_default_positions = {
    'top-axis': 'top',
    'left-axis': 'left',
    'horizontal-line': 'top',
    'heatmap': 'center',
    'horizontal-heatmap': 'top',
    'osm-tiles': 'center',
    'horizontal-bar': 'top',
    'horizontal-multivec': 'top',
    'horizontal-chromosome-labels': 'top',
    'viewport-projection-center': 'center'
}


class CombinedTrack:
    def __init__(self, tracks, position=None, height=100):
        '''
        The combined track contains multiple actual tracks as layers.

        Parameters
        ----------
        tracks: list
            A list of Tracks to add
        '''
        self.tracks = tracks
        self.tileset = None
        self.height = height

        # try to get the position from a subtrack
        self.position = position
        if position is None:
            for track in tracks:
                if track.position:
                    self.position = track.position
                    break

        self.viewconf = {
            'type': 'combined',
            'height': height,
            'contents': [t.to_dict() for t in self.tracks]
        }

    def to_dict(self):
        return self.viewconf


class Track:
    def __init__(
        self,
        track_type,
        position=None,
        tileset=None,
        height=None,
        width=None,
        tileset_uuid=None,
        server=None,
        file_url=None,
        filetype=None,
        fromViewUid=None,
        options={},
    ):

        """
        Add a track to a position.

        Parameters
        ----------
        track_type: string
            The type of track to add (e.g. "heatmap", "line")
        position: string
            One of 'top', 'bottom', 'center', 'left', 'right'
        tileset_uuid:
            The of uuid of the tileset being displayed in this track
        height: int
            The height of the track (in pixels)
        width: int
            The width of the track (in pixels)
        server: string
            The server name (usually just 'localhost')
        file_url: string
            An http accessible tileset file
        filetype: string
            The type of the remote tilesets (e.g. 'bigwig' or
            'cooler')
        options: {}

            The options to pass onto the track
        """
        new_track = {"type": track_type, "options": options}

        if tileset is not None:
            new_track["tilesetUid"] = tileset.uuid

        if server is not None and tileset_uuid is not None:
            if tileset is None:
                new_track["tilesetUid"] = tileset_uuid
                new_track["server"] = server
            else:
                print(
                    "Both a tileset object and server and tileset_uuid " +
                    "were provided, using the tileset object",
                    file=sys.stderr,
                )
        if server is not None and file_url is not None and filetype is not None:
            new_track["server"] = server
            new_track["fileUrl"] = file_url
            new_track["filetype"] = filetype
        if height is not None:
            new_track["height"] = height
        if width is not None:
            new_track['width'] = width
        if fromViewUid is not None:
            new_track['fromViewUid'] = fromViewUid

        if position is None:
            if track_type in track_default_positions:
                position = track_default_positions[track_type]

        self.tileset = tileset
        self.viewconf = new_track
        self.position = position
        self.tracks = None

    def change_attributes(self, **kwargs):
        '''
        Change an attribute of this track and return a new copy.
        '''
        new_track = Track(self.viewconf['type'])
        new_track.position = self.position
        new_track.tileset = self.tileset
        new_track.viewconf = json.loads(json.dumps(self.viewconf))
        new_track.viewconf = {**new_track.viewconf, **kwargs}

        return new_track

    def change_options(self, **kwargs):
        '''
        Change one of the track's options in the viewconf
        '''
        new_options = json.loads(json.dumps(self.viewconf['options']))
        new_options = {**new_options, **kwargs}

        return self.change_attributes(options=new_options)

    def to_dict(self):
        return self.viewconf


class View:
    def __init__(
        self,
        tracks=[],
        x=0,
        y=0,
        width=12,
        height=6,
        initialXDomain=None,
        initialYDomain=None,
        uid=None,
    ):
        """
        Add a new view

        Parameters
        --------
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
        if uid is None:
            uid = slugid.nice()

        self.tracks = tracks
        self.uid = uid

        self.viewconf = {
            "uid": uid,
            "tracks": {"top": [], "center": [], "left": [], "right": [], "bottom": []},
            "layout": {"w": width, "h": height, "x": x, "y": y},
        }

        if initialXDomain is not None:
            self.viewconf["initialXDomain"] = initialXDomain
        if initialYDomain is not None:
            self.viewconf["initialYDomain"] = initialYDomain

    def add_track(self, *args, **kwargs):
        """
        Add a track to a position.

        Parameters
        ----------
        track_type: string
            The type of track to add (e.g. "heatmap", "line")
        position: string
            One of 'top', 'bottom', 'center', 'left', 'right'
        tileset: hgflask.tilesets.Tileset
            The tileset to be plotted in this track
        server: string
            The server serving this track
        height: int
            The height of the track, if it is a top, bottom or a center track
        width: int
            The width of the track, if it is a left, right or a center track
        """
        new_track = Track(*args, **kwargs)
        self.tracks = self.tracks + [new_track]

    def to_dict(self):
        """
        Convert the existing track to a JSON representation.
        """
        viewconf = json.loads(json.dumps(self.viewconf))

        for track in self.tracks:
            if track.position is None:
                raise ValueError(
                    "Track has no position: {}".format(track.viewconf["type"])
                )
            viewconf["tracks"][track.position] += [track.to_dict()]

        return viewconf


class ViewConf:
    def __init__(self, views=[], location_syncs=[], zoom_syncs=[]):

        self.viewconf = {
            "editable": True,
            "views": [],
            "trackSourceServers": ["http://higlass.io/api/v1"],
            "locationLocks": {"locksByViewUid": {}, "locksDict": {}},
            "zoomLocks": {"locksByViewUid": {}, "locksDict": {}},
            "exportViewUrl": "http://higlass.io/api/v1/viewconfs",
        }

        self.views = views

        for location_sync in location_syncs:
            self.add_location_sync(location_sync)
        for zoom_sync in zoom_syncs:
            self.add_zoom_sync(zoom_sync)

        pass

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)

    def add_sync(self, locks_name, views_to_sync):
        lock_id = slugid.nice()
        for view_uid in [v.uid for v in views_to_sync]:
            if lock_id not in self.viewconf[locks_name]['locksDict']:
                self.viewconf[locks_name]['locksDict'][lock_id] = {}

            self.viewconf[locks_name]["locksDict"][lock_id][view_uid] = (1, 1, 1)
            self.viewconf[locks_name]["locksByViewUid"][view_uid] = lock_id

    def add_zoom_sync(self, views_to_sync=[]):
        self.add_sync("zoomLocks", views_to_sync)

    def add_location_sync(self, views_to_sync=[]):
        self.add_sync("locationLocks", views_to_sync)

    def add_view(self, *args, **kwargs):
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
        new_view = View(*args, **kwargs)

        for view in self.views:
            if view.uid == new_view.uid:
                raise ValueError("View with this uid already exists")

        self.views += [new_view]
        return new_view

    def location_lock(self, view_uid1, view_uid2):
        """
        Add a location lock between two views.
        """
        pass

    def to_dict(self):
        viewconf = json.loads(json.dumps(self.viewconf))

        for view in self.views:
            viewconf["views"] += [view.to_dict()]

        return viewconf


def datatype_to_tracktype(datatype):
    '''
    Infer a default track type from a data type. There can
    be other track types that can display a given data type.

    Parameters:
    -----------
    datatype: string
        A datatype identifier (e.g. 'matrix')

    Returns:
    --------
    string: A track type (e.g. 'heatmap')
    '''
    if datatype == 'matrix':
        return ('heatmap', 'center')
    if datatype == 'vector':
        return ('horizontal-bar', 'top')
    if datatype == 'gene-annotations':
        return ('horizontal-gene-annotations', 'top')
    if datatype == 'chromsizes':
        return ('horizontal-chromosome-labels', 'top')
    if datatype == '2d-rectangle-domains':
        return ('2d-rectangle-domains', 'center')
    if datatype == 'bedlike':
        return ('bedlike', 'top')

    return (None, None)
