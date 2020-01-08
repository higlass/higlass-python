from copy import deepcopy
import json
import slugid
import logging
import os


logger = logging.getLogger()
fhandler = logging.FileHandler(filename="higlass-python.log", mode="a")
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)

if "HIGLASS_PYTHON_DEBUG" in os.environ and os.environ["HIGLASS_PYTHON_DEBUG"]:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)


__all__ = ["Track", "CombinedTrack", "View", "ViewConf"]


_track_default_position = {
    "2d-rectangle-domains": "center",
    "bedlike": "top",
    "horizontal-bar": "top",
    "horizontal-chromosome-labels": "top",
    "horizontal-gene-annotations": "top",
    "horizontal-heatmap": "top",
    "horizontal-1d-heatmap": "top",
    "horizontal-line": "top",
    "horizontal-multivec": "top",
    "heatmap": "center",
    "left-axis": "left",
    "osm-tiles": "center",
    "top-axis": "top",
    "viewport-projection-center": "center",
    "viewport-projection-horizontal": "top",
}


_datatype_default_track = {
    "2d-rectangle-domains": "2d-rectangle-domains",
    "bedlike": "bedlike",
    "chromsizes": "horizontal-chromosome-labels",
    "gene-annotations": "horizontal-gene-annotations",
    "matrix": "heatmap",
    "vector": "horizontal-bar",
    "multivec": "horizontal-multivec",
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
    tileset : :class:`Tileset`
        A Tileset being displayed in this track
    file_url: str
        An http accessible tileset file
    filetype : str
        The type of the remote tilesets (e.g. 'bigwig', 'cooler', etc...)
    server : str, optional
        The server name (usually just 'localhost')
    height : int, optional
        The height of the track (in pixels)
    width : int, optional
        The width of the track (in pixels)
    options : dict, optional
        The options to pass onto the track

    """

    def __init__(
        self,
        track_type=None,
        position=None,
        tileset=None,
        file_url=None,
        filetype=None,
        options=None,
        **kwargs,
    ):
        if track_type is None:
            if "type" in kwargs:
                track_type = kwargs.pop("type")
            else:
                raise ValueError("Track type is required.")

        if not position:
            position = _track_default_position[track_type]

        self.position = position
        self.tileset = tileset

        # populate the actual config
        self.conf = {"type": track_type}
        if tileset is not None:
            self.conf["tilesetUid"] = tileset.uuid
        elif "tileset_uuid" in kwargs:
            self.conf["tilesetUid"] = kwargs.pop("tileset_uuid")
        elif file_url is not None and filetype is not None:
            self.conf["fileUrl"] = file_url
            self.conf["filetype"] = filetype

        if options is None:
            self.conf["options"] = {}
        else:
            self.conf["options"] = deepcopy(options)

        self.conf.update(kwargs)

        if "uid" not in self.conf:
            self.conf["uid"] = slugid.nice()

    @property
    def uid(self):
        return self.conf["uid"]

    @property
    def options(self):
        return self.conf["options"]

    @property
    def type(self):
        return self.conf["type"]

    def change_attributes(self, **kwargs):
        """
        Change an attribute of this track and return a new copy.
        """
        conf = self.conf.copy()
        conf.update(kwargs)
        return self.__class__(
            conf["type"], position=self.position, tileset=self.tileset, **conf
        )

    def change_options(self, **kwargs):
        """
        Change one of the track's options in the viewconf
        """
        options = self.conf["options"].copy()
        options.update(kwargs)
        return self.change_attributes(options=options)

    def __add__(self, other):
        """Overload the + operator to create combined tracks."""
        new_tracks = []

        if self.conf["type"] == "combined":
            # this is a combined track
            for track in self.tracks:
                new_tracks += [track.copy()]
        else:
            new_tracks += [self]

        if other.conf["type"] == "combined":
            for track in other.tracks:
                new_tracks += [track.copy()]
        else:
            new_tracks += [other.copy()]

        return CombinedTrack(new_tracks)

    def __truediv__(self, other):
        return DividedTrack(self, other,)

    @classmethod
    def from_dict(cls, conf):
        return cls(**conf)

    def to_dict(self):
        return self.conf.copy()

    def copy(self):
        return Track(**self.to_dict())


class DividedTrack(Track):
    """A track representing one tileset divided by another.

    Only works with some tileset types.
    """

    def __init__(
        self, numerator, denominator, *args, **kwargs,
    ):
        """This track is created using two tilesets.

        Parameters
        ----------
        numerator (tileset):
            The tileset to be divided
        denominator (tileset):
            The tileset to divide by
        """
        if numerator.conf["type"] != denominator.conf["type"]:
            raise ValueError(
                f"Different track types: {self.conf['type']}, {other.conf['type']}"
            )

        if json.dumps(numerator.conf["options"]) != denominator.dumps(
            other.conf["options"]
        ):
            logger.warn(
                "Tracks have different options, " "so we're using the first track's"
            )

        numerator_server = numerator.conf["server"]
        numerator_uuid = numerator.conf["tilesetUid"]

        denominator_server = denominator.conf["server"]
        denominator_uuid = denominator.conf["tilesetUid"]

        track_type = numerator.conf["type"]
        position = numerator.position
        options = numerator.conf["options"]
        height = numerator.conf["height"] if "height" in numerator.conf else None

        data_config = {
            "type": "divided",
            "children": [
                {"server": numerator_server, "tilesetUid": numerator_uuid},
                {"server": denominator_server, "tilesetUid": denominator_uuid},
            ],
        }

        super().__init__(
            data=data_config,
            type=track_type,
            position=position,
            options=options,
            height=height,
            *args,
            **kwargs,
        )

    def change_attributes(self, **kwargs):
        """
        Change an attribute of this track and return a new copy.
        """
        conf = self.conf.copy()
        conf.update(kwargs)

        return Track(conf["type"]).from_dict(conf)


class CombinedTrack(Track):
    def __init__(self, tracks, position=None, height=None, **kwargs):
        """
        The combined track contains multiple actual tracks as layers.

        Parameters
        ----------
        tracks: list
            A list of Tracks to add
        """
        self.tracks = tracks
        self.tileset = None

        # try to get the position from a subtrack
        self.position = position
        if position is None:
            for track in tracks:
                if track.position:
                    self.position = track.position
                    break

        for track in tracks:
            if track.conf["type"] == "viewport-projection":
                track.conf["type"] = position_to_viewport_projection_type(self.position)
                track.position = self.position
        #
        # if no height is specified try to infer it from
        # the containing tracks
        if not height:
            for track in tracks:
                if "height" in track.conf and track.conf["height"]:
                    if not height:
                        height = track.conf["height"]
                    else:
                        height = max(height, track.conf["height"])

        if height:
            self.height = height
            self.conf = {"type": "combined", "height": height}
        else:
            self.conf = {"type": "combined"}

    @classmethod
    def from_dict(cls, conf):
        if "contents" in conf:
            conf = conf.copy()
            contents = conf.pop("contents")
            tracks = [Track.from_dict(track_conf) for track_conf in contents]
        else:
            tracks = []
        return cls(tracks, **conf)

    def to_dict(self):
        conf = self.conf.copy()
        conf["contents"] = [t.to_dict() for t in self.tracks]
        return conf


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
        overlays=[],
    ):
        if uid is None:
            uid = slugid.nice()
        self.uid = uid

        self.conf = {
            "uid": uid,
            "tracks": {"top": [], "center": [], "left": [], "right": [], "bottom": []},
            "layout": {"w": width, "h": height, "x": x, "y": y},
        }
        if initialXDomain is not None:
            self.conf["initialXDomain"] = initialXDomain
        if initialYDomain is not None:
            self.conf["initialYDomain"] = initialYDomain

        self._track_position = {}

        for track in tracks:
            if isinstance(track, (tuple, list)):
                new_track = CombinedTrack(track)
                self.add_track(new_track)
            else:
                self.add_track(track)

        for i, overlay in enumerate(overlays):
            # The uids need to be unique so if no uid is available we need to
            # define a unique uid before calling `self.add_overlay`.
            overlay["uid"] = overlay.get("uid", "overlay-{}".format(i))
            self.add_overlay(overlay)

    @property
    def tracks(self):
        return list(self._track_position.keys())

    def add_track(self, track, position=None):
        """
        Add a track to a position.

        Parameters
        ----------
        track : :class:`Track`
            Track to add.
        position : {'top', 'bottom', 'center', 'left', 'right'}
            Location of track on the view. If not provided, we look for an
            assigned ``position`` attribute in ``track``. If it does not exist,
            we fall back on a default position if the track type has one.

        """
        if position is None:
            if track.position is not None:
                position = track.position
            elif track.type in _track_default_position:
                position = _track_default_position[track.type]
            else:
                raise ValueError("A track position is required.")
        self._track_position[track] = position

    def create_track(self, track_type, **kwargs):
        if track_type == "combined":
            klass = CombinedTrack
        else:
            klass = Track
        position = kwargs.pop("position", None)
        track = klass(track_type=track_type, **kwargs)
        self.add_track(track, position)
        return track

    @classmethod
    def from_dict(cls, conf):
        layout = conf.get("layout", {})
        self = cls(
            x=layout.get("x", 0),
            y=layout.get("y", 0),
            width=layout.get("w", 12),
            height=layout.get("h", 6),
            initialXDomain=conf.get("initialXDomain", None),
            initialYDomain=conf.get("initialYDomain", None),
            uid=conf.get("uid", None),
            overlays=conf.get("overlays", []),
        )
        for position in conf.get("tracks", {}):
            for track_conf in conf["tracks"][position]:
                if track_conf["type"] == "combined":
                    klass = CombinedTrack
                else:
                    klass = Track

                # position has to be passed in as part of the parameter
                # array so that the constructor can be called with it as
                # a parameter
                self.add_track(
                    track=klass.from_dict({"position": position, **track_conf})
                )
        return self

    def to_dict(self):
        """
        Convert the existing track to a JSON representation.
        """
        conf = json.loads(json.dumps(self.conf))
        for track, position in self._track_position.items():
            conf["tracks"][position].append(track.to_dict())
        return conf

    def add_overlay(self, overlay):
        if "overlays" not in self.conf:
            self.conf["overlays"] = []

        try:
            options = overlay.get("options", {})
            overlay_conf = {
                "uid": overlay.get("uid", "overlay"),
                "includes": overlay.get("includes", []),
                "type": overlay.get("type", ""),
                "options": {"extent": overlay.get("extent", [])},
            }
            overlay_conf["options"].update(options)
            self.conf["overlays"].append(overlay_conf)
        except KeyError:
            pass


class ViewConf(Component):
    """Configure a dashboard"""

    def __init__(
        self, views=[], location_syncs=[], value_scale_syncs=[], zoom_syncs=[]
    ):

        self.conf = {
            "editable": True,
            "views": [],
            "trackSourceServers": ["http://higlass.io/api/v1"],
            "locationLocks": {"locksByViewUid": {}, "locksDict": {}},
            "valueScaleLocks": {"locksByViewUid": {}, "locksDict": {}},
            "zoomLocks": {"locksByViewUid": {}, "locksDict": {}},
            "exportViewUrl": "http://higlass.io/api/v1/viewconfs",
        }

        self._views_by_id = {}

        for view in views:
            self.add_view(view)

        for location_sync in location_syncs:
            self.add_location_sync(location_sync)

        for value_scale_sync in value_scale_syncs:
            self.add_value_scale_sync(value_scale_sync)

        for zoom_sync in zoom_syncs:
            self.add_zoom_sync(zoom_sync)

    @property
    def views(self):
        return list(self._views_by_id.values())

    @property
    def default_view(self):
        """Default view of the view config

        The default view equals the first view if only one view exist.

        Returns:
            View -- View instance or ``None`` if more than one view exists.
        """
        if len(self.views) == 1:
            return self.views[0]
        return None

    def _combine_view_track_uid(self, view_uid, track_uid):
        return f"{view_uid}.{track_uid}"

    def _extract_view_track_uids(self, definition):
        if isinstance(definition, tuple):
            # definition is a tuple of a view and a track instance
            view_uid = definition[0].uid
            track_uid = definition[1].uid
        elif isinstance(definition, Track):
            # definition is a track instance which assumes that only one view
            # exists
            track_uid = definition.uid
        elif isinstance(definition, str):
            # definition is a string
            uids = definition.split(".")
            if len(uids) == 2:
                view_uid, track_uid = uids
            else:
                track_uid = uids[0]
        else:
            logger.warning("Could not extract view and track UID")
            track_uid = None
            view_uid = None

        if self.default_view is not None:
            logger.info("Default view is used")
            view_uid = self.default_view.uid

        return view_uid, track_uid

    def _add_sync(self, lock_group, lock_id, view_uids):
        for view_uid in view_uids:
            if lock_id not in self.conf[lock_group]["locksDict"]:
                self.conf[lock_group]["locksDict"][lock_id] = {}
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

    def add_value_scale_sync(self, tracks_to_sync):
        locks_map = self.conf["valueScaleLocks"]["locksByViewUid"]
        locks_dict = self.conf["valueScaleLocks"]["locksDict"]
        lock_id = slugid.nice()

        for definition in tracks_to_sync:
            v_uid, t_uid = self._extract_view_track_uids(definition)

            if v_uid is None or t_uid is None:
                # If no view UID is found the definition seems to be broken
                logger.warning("View or track definition is broken")
                continue

            vt_uid = self._combine_view_track_uid(v_uid, t_uid)

            if lock_id not in locks_dict:
                locks_dict[lock_id] = {}

            locks_dict[lock_id][vt_uid] = {"view": v_uid, "track": t_uid}
            locks_map[vt_uid] = lock_id

    def add_view(self, view):
        """
        Add a new view

        Parameters
        ----------
        view: :class:`View`
            View object to add

        """
        for uid in self._views_by_id.keys():
            if uid == view.uid:
                raise ValueError("View with this uid already exists")
        self._views_by_id[view.uid] = view

    def create_view(self, *args, **kwargs):
        view = View(*args, **kwargs)
        self.add_view(view)
        return view

    @classmethod
    def from_link(cls, url):

        from urllib.parse import urlsplit, urlunsplit, parse_qs
        import requests

        # parts: 'scheme://netloc/path?query#fragment'
        parts = urlsplit(url)
        query = parse_qs(parts.query)
        if parts.path.strip("/") == "app":
            if "config" not in query:
                raise ValueError("Viewconf ID not found in query")
            conf_id = query["config"][0]
        elif parts.path.strip("/") in ("api/v1/viewconfs", "l", "link"):
            if "d" not in query:
                raise ValueError("Viewconf ID not found in query")
            conf_id = query["d"][0]
        else:
            raise ValueError("Not a valid viewconf server")

        endpoint = urlunsplit(
            (parts.scheme, parts.netloc, "api/v1/viewconfs", "d=" + conf_id, "")
        )

        conf = requests.get(endpoint).json()

        return cls.from_dict(conf)

    @classmethod
    def from_dict(cls, conf):
        self = cls()

        for view_dct in conf.get("views", []):
            self.add_view(View.from_dict(view_dct))

        locks = conf.get("locationLocks", {}).get("locksDict", {})
        for lock_id, attrs in locks.items():
            self._add_sync("locationLocks", lock_id, attrs.keys())

        locks = conf.get("valueScaleLocks", {}).get("locksDict", {})
        for lock_id, attrs in locks.items():
            self._add_sync("valueScaleLocks", lock_id, attrs.keys())

        locks = conf.get("zoomLocks", {}).get("locksDict", {})
        for lock, attrs in locks.items():
            self._add_sync("zoomLocks", lock_id, attrs.keys())

        return self

    def to_dict(self):
        conf = json.loads(json.dumps(self.conf))
        for view in self.views:
            conf["views"].append(view.to_dict())
        return conf


def tracktype_default_position(tracktype: str):
    """
    Get the default track position for a track type.

    For example, default position for a heatmap is 'center'.
    If the provided track type has no known default position
    return None.

    Parameters
    ----------
    tracktype: str
        The track type to check

    Returns
    -------
    str:
        The default position
    """
    if tracktype in _track_default_position:
        return _track_default_position[tracktype]

    return None


def datatype_to_tracktype(datatype):
    """
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

    """
    track_type = _datatype_default_track.get(datatype, None)
    position = _track_default_position.get(track_type, None)
    return track_type, position


def position_to_viewport_projection_type(position):
    if position == "center":
        track_type = "viewport-projection-center"
    elif position == "top" or position == "bottom":
        track_type = "viewport-projection-horizontal"
    elif position == "left" or position == "right":
        track_type = "viewport-projection-vertical"
    else:
        track_type = "viewport-projection"

    return track_type


class ViewportProjection(Track):
    def __init__(self, view, position=None):
        self.position = position
        track_type = position_to_viewport_projection_type(position)
        self.conf = {"type": track_type, "fromViewUid": view.uid}
        self.view = view

        if "uid" not in self.conf:
            self.conf["uid"] = slugid.nice()

    def copy(self):
        """Copy this track."""
        return ViewportProjection(self.view, self.position)
