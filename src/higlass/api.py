from __future__ import annotations

import functools
from collections import defaultdict
from typing import (
    ClassVar,
    Generic,
    Literal,
    TypeVar,
    Union,
    cast,
    overload,
)

import higlass_schema as hgs
from pydantic import RootModel

import higlass._utils as utils

__all__ = [
    "CombinedTrack",
    "EnumTrack",
    "HeatmapTrack",
    "IndependentViewportProjectionTrack",
    "PluginTrack",
    "TrackT",
    "View",
    "ViewT",
    "Viewconf",
    "combine",
    "concat",
    "divide",
    "hconcat",
    "lock",
    "track",
    "vconcat",
    "view",
]


## Mixins

# Can't figure out a good way to type these classes.
# We ignoring the errors in the parameter signature
# mean we can get good type information within the
# function and return types are inferred for end users.


class _PropertiesMixin:
    def properties(
        self: utils.ModelT,  # type: ignore
        inplace: bool = False,
        **fields,  # type: ignore
    ) -> utils.ModelT:  # type: ignore
        """Configures top-level properties.

        Updates top-level properties for a Track, View, or Viewconf. This
        is really a convenience to allow method chaining/derived objects
        to be created without multiple lines of mutating the classes. For
        example,

        >>> view = hg.view(hg.track("heatmap"))
        >>> updated_view = view.properties(zoomFixed=True)
        >>> assert view.uid != updated_view.uid
        >>> assert view.zoomFixed is None
        >>> assert updated_view.zoomFixed is True

        inplace : bool, optional
            Whether to modify the existing track in place or return
            a new track with the options applied (default: `False`).

        **fields : dict
            The updated properties for .

        Returns
        -------
        track : A track with the the newly specified track options.

        """
        model = self if inplace else utils.copy_unique(self)
        for k, v in fields.items():
            setattr(model, k, v)
        return model


class _OptionsMixin:
    def opts(
        self: TrackT,  # type: ignore
        inplace: bool = False,
        **options,
    ) -> TrackT:  # type: ignore
        """Configures options for a Track.

        A convenience method to update `track.options`.

        Parameters
        ----------
        inplace : bool, optional
            Whether to modify the existing track in place or return
            a new track with the options applied (default: `False`).

        **options : dict
            Options to pass down to the underlying track object.

        Returns
        -------
        track : A track with the the newly specified track options.

        Examples
        --------
        >>> track = hg.track("heatmap")
        >>> derived = track.opts(colorRange=["rgba(255,255,255,1)", "rgba(0,0,0,1)"])
        >>> assert track.options is None
        >>> assert isinstance(derived.options["colorRange"], list)

        """
        track = self if inplace else utils.copy_unique(self)
        if track.options is None:
            track.options = {}
        track.options.update(options)
        return track


## Extend higlass-schema classes


class EnumTrack(hgs.EnumTrack, _OptionsMixin, _PropertiesMixin):
    """Represents a generic track."""

    ...


class HeatmapTrack(hgs.HeatmapTrack, _OptionsMixin, _PropertiesMixin):
    """Represets a specialized heatmap track."""

    ...


class IndependentViewportProjectionTrack(
    hgs.IndependentViewportProjectionTrack,
    _OptionsMixin,
    _PropertiesMixin,
):
    """Represents a view-independent viewport projection track."""

    ...


class CombinedTrack(hgs.CombinedTrack, _OptionsMixin, _PropertiesMixin):
    """Represents a track combining multiple tracks."""

    ...


class PluginTrack(hgs.BaseTrack, _OptionsMixin, _PropertiesMixin):
    """Represents an unknown plugin track."""

    plugin_url: ClassVar[str]


Track = Union[
    HeatmapTrack,
    IndependentViewportProjectionTrack,
    EnumTrack,
    CombinedTrack,
    PluginTrack,
]

TrackT = TypeVar("TrackT", bound=Track)


class View(hgs.View[TrackT], _PropertiesMixin, Generic[TrackT]):
    """Represets a HiGlass View that is generic over the inner tracks."""

    def domain(
        self,
        x: hgs.Domain | None = None,
        y: hgs.Domain | None = None,
        inplace: bool = False,
    ):
        """Configures the view x and/or y domain(s).

        Parameters
        ----------
        x : tuple[float, float], optional
            The x domain for the view (default: `None`)

        y : tuple[float, float], optional
            The y domain for the view (default: `None`)

        inplace : bool, optional
            Whether to modify this view inplace. If `False` (default),
            a new view is created and returned with the domains
            applied (default: `False`)

        Returns
        -------
        view : a View with the updated x & y domains

        """
        view = self if inplace else utils.copy_unique(self)
        if x is not None:
            view.initialXDomain = x
        if y is not None:
            view.initialYDomain = y
        return view

    def __or__(self, other: View[TrackT] | Viewconf[TrackT]):
        """Horizontally concatenate with another view or viewconf.

        A convenience method for `hg.hconcat`.

        Parameters
        ----------
        other : View | Viewconf
            The other view or viewconf to combine with.

        Returns
        -------
        viewconf : A combined Viewconf

        """
        return hconcat(self, other)

    def __truediv__(self, other: View[TrackT] | Viewconf[TrackT]):
        """Vertically concatenate two Views.

        A convenience method for `hg.vconcat`.

        Parameters
        ----------
        other : View | Viewconf
            The other view or viewconf to combine with.

        Returns
        -------
        viewconf : A combined Viewconf

        """
        return vconcat(self, other)

    def clone(self):
        """Clone the the View instance.

        Inserts a unique uuid so the view can be uniquely identified in the front end.

        Returns
        -------
        view : A copy of the original view with a new uuid

        """
        return utils.copy_unique(self)

    def viewconf(self, **kwargs):
        """Consumes the current View into a top-level view config.

        Returns
        -------
        viewconf : A top-level HiGlass Viewconf.

        """
        return Viewconf[TrackT](views=[self], **kwargs)

    def _repr_mimebundle_(self, include=None, exclude=None):
        """ "Displays the view in an IPython environment."""
        return self.viewconf()._repr_mimebundle_(include, exclude)

    def widget(self, **kwargs):
        """Create a Jupyter Widget display for this view.

        Casts the view into a top-level view config which can be displayed.

        Returns
        -------
        widget : A HiGlassWidget instance
        """
        return self.viewconf().widget(**kwargs)

    def project(
        self,
        view: View,
        on: Literal["center", "top", "bottom", "left", "right"] = "center",
        inplace: bool = False,
        **kwargs,
    ):
        """Project a different viewport onto this view.

        Creates a viewport-projection track whos bounds are synchonrized
        with an existing, separate view.

        Parameters
        ----------
        view : View
            The view with the desired viewport to project.

        on : Literal["center", "top", "bottom", "left", "right"], optional
            Where to project the viewport on this view (default: "center").

        inplace : bool
            Whether to modify this view inplace, or alternatively return
            a new view (default: `False`).

        **kwargs : dict
            Additional parameters for the created viewport-projection track.

        Returns
        -------
        view : A view with a new viewport-projection track.
        """
        new_view = self if inplace else utils.copy_unique(self)

        # projection track type from position
        if on == "center":
            track_type = "viewport-projection-center"
        elif on == "top" or on == "bottom":
            track_type = "viewport-projection-horizontal"
        elif on == "left" or on == "right":
            track_type = "viewport-projection-vertical"
        else:
            raise ValueError("Not possible")

        if getattr(new_view.tracks, on) is None:
            setattr(new_view.tracks, on, [])

        trk = track(type_=track_type, fromViewUid=view.uid, **kwargs)
        getattr(new_view.tracks, on).append(trk)

        return new_view


ViewT = TypeVar("ViewT", bound=View)


def gather_plugin_urls(views: list[ViewT]) -> list[str]:
    """Inspect tracks and extract plugin urls to inject into HTML."""
    plugin_urls = {}
    for view in views:
        for _, track in view.tracks:
            if isinstance(track, PluginTrack):
                plugin_urls[track.type] = track.plugin_url
    return list(plugin_urls.values())


class Viewconf(hgs.Viewconf[View[TrackT]], _PropertiesMixin, Generic[TrackT]):
    """Represents a top-level viewconfig, or a complete HiGlass visualization."""

    def _repr_mimebundle_(self, include=None, exclude=None):
        """Displays the view config in an IPython environment."""
        return self.widget()._repr_mimebundle_()

    def widget(self, **kwargs):
        """Create a Jupyter Widget display for this view config."""
        from higlass._widget import HiGlassWidget

        return HiGlassWidget(
            viewconf=self.model_dump(),
            plugin_urls=[] if self.views is None else gather_plugin_urls(self.views),
            **kwargs,
        )

    @classmethod
    def from_url(cls, url: str, **kwargs):
        """Load a viewconf via URL and construct a Viewconf.

        Makes an HTTP request.

        Parameters
        ----------
        url : str
            The URL for a JSON HiGlass view config.

        **kwargs : dict
            Options for the `urllib.Request` instance.

        Returns
        -------
        viewconf : The parsed view config

        """
        import urllib.request as urllib

        request = urllib.Request(url, **kwargs)
        with urllib.urlopen(request) as response:
            raw = response.read()

        return cls.model_validate_json(raw)

    def locks(
        self,
        *locks: hgs.Lock | hgs.ValueScaleLock,
        zoom: list[hgs.Lock] | hgs.Lock | None = None,
        location: list[hgs.Lock] | hgs.Lock | None = None,
        value_scale: list[hgs.ValueScaleLock] | hgs.ValueScaleLock | None = None,
        inplace: bool = False,
    ):
        """Specify view locks.

        Parameters
        ----------

        *locks : hgs.Lock | hgs.ValueScaleLock, optional
            A set of either zoom/location or value scale locks to add. Instances
            of `hgs.Lock` will synchronize _both_ zoom and location for the views
            included in the lock. If you'd like to synchronize just zoom or location,
            use the explicit keyword arguments below.

        zoom : hgs.Lock | list[hgs.Lock], optional
            A lock or set of locks to synchronize only the zoom.

        location : hgs.Lock | list[hgs.Lock], optional
            A lock or set of locks to synchronize only the location.

        value_scale : hgs.ValueScaleLock | list[hgs.ValueScaleLock], optional
            A single or set of value-scale locks.

        inplace : bool, optional
            Whether to modify the viewconf in place or return a new viewconf
            with the locks applied (default: `False`)

        Returns
        -------

        viewconf : A Viewconf with the synchronized views.


        Examples
        --------

        >>> view1 = hg.view(hg.track("heatmap"))
        >>> view2 = hg.view(hg.track("heatmap"))
        >>> # create an abstract lock for two views
        >>> view_lock = hg.lock(view1, view2)
        >>> # lock location & zoom
        >>> (view1 | view2).lock(view_lock)
        >>> # lock only zoom
        >>> (view1 | view2).lock(zoom=view_lock)
        >>> # lock only location
        >>> (view1 | view2).lock(location=view_lock)

        """
        conf = self if inplace else utils.copy_unique(self)

        zoom = utils.ensure_list(zoom)
        location = utils.ensure_list(location)
        value_scale = utils.ensure_list(value_scale)

        shared_locks: list[hgs.Lock] = []
        for lock in locks:
            if isinstance(lock, hgs.Lock):
                shared_locks.append(lock)
            else:
                value_scale.append(lock)

        zoom.extend(shared_locks)
        location.extend(shared_locks)

        if conf.zoomLocks is None:
            conf.zoomLocks = hgs.ZoomLocks()

        for lock in zoom:
            assert isinstance(lock.uid, str)
            conf.zoomLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock:
                conf.zoomLocks.locksByViewUid[vuid] = lock.uid

        if conf.locationLocks is None:
            conf.locationLocks = hgs.LocationLocks()

        for lock in location:
            assert isinstance(lock.uid, str)
            conf.locationLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock:
                conf.locationLocks.locksByViewUid[vuid] = lock.uid

        if conf.valueScaleLocks is None:
            conf.valueScaleLocks = hgs.ValueScaleLocks()

        for lock in value_scale:
            assert isinstance(lock.uid, str)
            conf.valueScaleLocks.locksDict[lock.uid] = lock
            for vuid, _ in lock:
                conf.valueScaleLocks.locksByViewUid[vuid] = lock.uid

        return conf

    def __or__(self, other: View[TrackT] | Viewconf[TrackT]) -> Viewconf[TrackT]:
        """Horizontally concatenate with another view or viewconf.

        A convenience method for `hg.hconcat`.

        Parameters
        ----------
        other : View | Viewconf
            The other view or viewconf to combine with.

        Returns
        -------
        viewconf : A combined Viewconf

        """
        return hconcat(self, other)

    def __truediv__(self, other: View[TrackT] | Viewconf[TrackT]) -> Viewconf[TrackT]:
        """Vertically concatenate with another view or viewconf.

        A convenience method for `hg.hconcat`.

        Parameters
        ----------
        other : View | Viewconf
            The other view or viewconf to combine with.

        Returns
        -------
        viewconf : A combined Viewconf

        """
        return vconcat(self, other)


TrackTA = TypeVar("TrackTA", bound=Track)
TrackTB = TypeVar("TrackTB", bound=Track)


def concat(
    method: Literal["horizontal", "vertical"],
    a: View[TrackTA] | Viewconf[TrackTA],
    b: View[TrackTB] | Viewconf[TrackTB],
) -> Viewconf[TrackTA | TrackTB]:
    """Concatenate two views or separate viewconfs together.

    Uses the layout of one view or the total bounds of all views in one
    viewconf to offset the other view/viewconf.

    Parameters
    ----------
    method : Literal["horizontal", "vertical"]
        How to concatenate views/viewconfs.

    a : View | Viewconf
        A view or viewconf to combine.

    b : View | Viewconf
        The other view or viewconf to combine.

    Returns
    -------
    viewconf : A combined viewconf containing multiple views.

    """
    a = a.viewconf() if isinstance(a, View) else a
    assert a.views is not None

    b = b.viewconf() if isinstance(b, View) else b
    assert b.views is not None

    if method == "vertical":

        def mapper(view):
            return view.layout.y + view.layout.h

        field = "y"
    elif method == "horizontal":

        def mapper(view):
            return view.layout.x + view.layout.w

        field = "x"
    else:
        raise ValueError("concat method must be 'vertical' or 'horizontal'.")

    # gather views and adjust layout
    views = [v.model_copy(deep=True) for v in b.views]
    offset = 0 if a.views is None else max(map(mapper, a.views))
    for view in views:
        curr = getattr(view.layout, field)
        setattr(view.layout, field, curr + offset)

    a.views.extend(views)  # type: ignore

    # merge locks
    for lockattr in ["zoomLocks", "valueScaleLocks", "locationLocks"]:
        locks = getattr(b, lockattr)
        if locks:
            if getattr(a, lockattr) is None:
                setattr(a, lockattr, locks.model_copy(deep=True))
            else:
                getattr(a, lockattr).locksByViewUid.update(locks.locksByViewUid)
                getattr(a, lockattr).locksDict.update(locks.locksDict)

    return cast(Viewconf[Union[TrackTA, TrackTB]], a)


hconcat = functools.partial(concat, "horizontal")

vconcat = functools.partial(concat, "vertical")


## Top-level functions to easily create tracks,

# TODO: register plugins globally to work here?


class _TrackCreator(RootModel):
    """Create track instances from their track type.

    Used internally by `hg.track` to leverage pydantic's ability to get
    the appropriate base model by the track type.

    Example:
    -------
    >>> assert isinstance(_TrackCreator(type="heatmap").root, HeatmapTrack)
    """

    root: Track


@overload
def track(type_: hgs.EnumTrackType, uid: str | None = None, **kwargs) -> EnumTrack: ...


@overload
def track(
    type_: Literal["heatmap"], uid: str | None = None, **kwargs
) -> HeatmapTrack: ...


@overload
def track(type_: str, uid: str | None = None, **kwargs) -> PluginTrack: ...


def track(
    type_: hgs.EnumTrackType | Literal["heatmap"] | str,
    uid: str | None = None,
    **kwargs,
) -> Track:
    """Create a HiGlass track.

    Parameters
    ----------
    type_ : str
        The track type to create

    uid: str, optional
        A unique id for the track. If unspecified (default), a unique id is given
        internally.

    **kwargs: dict
        Other top-level track properties.

    Returns
    -------
    track :  An instance of an hg.Track
    """
    if uid is None:
        uid = utils.uid()
    data = dict(type=type_, uid=uid, **kwargs)
    return _TrackCreator.model_validate(data).root


def view(
    *_tracks: TrackT | tuple[TrackT, utils.TrackPosition] | hgs.Tracks[TrackT],
    x: int = 0,
    y: int = 0,
    width: int = 12,
    height: int = 6,
    tracks: hgs.Tracks[TrackT] | None = None,
    layout: hgs.Layout | None = None,
    uid: str | None = None,
    **kwargs,
) -> View[TrackT]:
    """Create a HiGlass view from multiple tracks.

    Parameters
    ----------
    *_tracks : Track | tuple[Track, str] | hgs.Tracks[Track]
        The tracks to include in the view. Can be 1) separate track objects
        (position inferred), 2) explicit (Track, position) tuples, or 3.) a
        `higlass_schema.Tracks` Object specifying all tracks and positions.

    x : int, optional
        The x position of the view in the HiGlass grid (default: 0). Used to
        created a Layout if none is provided.

    y : int, optional
        The y position of the view in the HiGlass grid (default: 0). Used to
        created a Layout if none is provided.

    width : int, optional
        The width of the view (default: 12). Used to created a Layout if none is
        provided.

    height : int, optional
        The height of the view (default: 6). Used to created a Layout if none is
        provided.

    layout : hgs.Layout, optional
        An explicit layout for the view (default: None). If provided the `x`, `y`,
        `width`, and `height` parameters are ignored.

    uid: str, optional
        A unique id for the view. If unspecified (default), a unique id is automatically
        generated internally.

    **kwargs: dict
        Other top-level view properties.

    Returns
    -------
    view :  An instance of an hg.View
    """
    if layout is None:
        layout = hgs.Layout(x=x, y=y, w=width, h=height)
    else:
        layout = hgs.Layout(**layout.model_dump())

    if tracks is None:
        data = defaultdict(list)
    else:
        data = defaultdict(list, tracks.model_dump())

    for track in _tracks:
        if isinstance(track, hgs.Tracks):
            track = track.model_dump()
            for position, track_list in track.items():
                data[position].extend(track_list)
        else:
            if isinstance(track, tuple):
                track, position = track
            else:
                position = utils.track_default_position.get(track.type)
                if position is None:
                    raise ValueError("No default track type")

            data[position].append(track)

    if uid is None:
        uid = utils.uid()

    return View[TrackT](
        layout=layout,
        tracks=hgs.Tracks[TrackT](**data),
        uid=uid,
        **kwargs,
    )


def combine(t1: Track, t2: Track, uid: str | None = None, **kwargs) -> CombinedTrack:
    """A utility to create a CombinedTrack from two other tracks.

    Parameters
    ----------

    t1 : hg.Track
        The first of two tracks to combine.

    t2 : hg.Track
        The second of two tracks to combine.

    uid : str, optional
        A unique id for the newly created CombinedTrack.

    **kwargs : dict
        Additional properties to pass to the CombinedTrack constructor.

    Returns
    -------

    combined_track : An CombinedTrack with two children tracks.

    """
    if uid is None:
        uid = utils.uid()

    if isinstance(t1, CombinedTrack):
        copy = CombinedTrack(**t1.model_dump())
        copy.contents.append(t2.__class__(**t2.model_dump()))
        for key, val in kwargs.items():
            setattr(copy, key, val)
        return copy

    return CombinedTrack(
        type="combined",
        uid=uid,
        contents=[track.__class__(**track.model_dump()) for track in (t1, t2)],
        **kwargs,
    )


T = TypeVar("T", bound=Union[EnumTrack, HeatmapTrack])


def divide(t1: T, t2: T, **kwargs) -> T:
    """A utility to create a divided track.

    Tracks must the the same type.

    Parameters
    ----------

    t1 : hg.EnumTrack | hg.HeatmapTrack
        The first track to divide by the other.

    t2 : hg.EnumTrack | hg.HeatmapTrack
        The other track.

    **kwargs : dict
        Additional properties to pass to the newly created track.

    Returns
    -------

    divided_track : An identical track with "divided" data sources.

    """
    assert t1.type == t2.type, "divided tracks must be same type"
    assert isinstance(t1.tilesetUid, str)
    assert isinstance(t1.server, str)

    assert isinstance(t2.tilesetUid, str)
    assert isinstance(t2.server, str)

    copy = utils.copy_unique(t1)
    copy.tilesetUid = None
    copy.server = None
    copy.data = hgs.Data(
        type="divided",
        children=[
            {
                "tilesetUid": track.tilesetUid,
                "server": track.server,
            }
            for track in (t1, t2)
        ],
    )
    # overrides
    for key, val in kwargs.items():
        setattr(copy, key, val)
    return copy


@overload
def lock(*views: View, uid: str | None = None) -> hgs.Lock:
    """Create an abstract lock linking two or more views.

    Parameters
    ----------

    *views : View
        Two or more views to synchronize with this lock.

    uid : str, optional
        An (optional) unique id for this lock.

    Returns
    -------

    lock : An abstract lock linking two or more views.

    """
    ...


@overload
def lock(
    *pairs: tuple[View, Track],
    uid: str | None = None,
    ignoreOffScreenValues: bool | None = None,
) -> hgs.ValueScaleLock:
    """Create an abstract value-scale lock linking one or more (View, Track) pairs.

    Parameters
    ----------

    *pairs : tuple[View, Track]
        One or more (View, Track) pairs specifying a Track whos values should
        be used to scale all tracks within the View.

    uid : str, optional
        An (optional) unique id for this lock.

    ignoreOffScreenValues : bool, optional
        Whether to ignore off screen values when scaling the view.

    Returns
    -------

    lock : A value-scale lock defining how the tracks in a View should be scaled by
        by a particular track.

    """
    ...


def lock(*data, uid: str | None = None, **kwargs):
    """Create an abstract lock or value-scale lock.

    Overloaded to either return a `hgs.Lock` or `hgs.ValueScaleLock` depending on
    the arguments. See `Viewconf.locks` for how to use the created locks in
    your top-level view config.

    Examples
    --------

    Create an abstract lock linking two or more separate views.

    >>> view1 = hg.view(hg.track("heatmap"))
    >>> view2 = hg.view(hg.track("heatmap"))
    >>> lock = hg.lock(view1, view2)

    Create a value-scale lock, scaling two views by the values of a particular track.

    >>> t1 = hg.track("heatmap")
    >>> t2 = hg.track("heatmap")
    >>> view1 = hg.view(t1, t2)
    >>> view2 = hg.view(t1, t2)
    >>> value_scale_lock = hg.lock((view1, t2), (view2, t2))

    """
    assert len(data) >= 1
    if uid is None:
        uid = utils.uid()
    if isinstance(data[0], View):
        lck = hgs.Lock(uid=uid)
        for view in data:
            assert isinstance(view.uid, str)
            setattr(lck, view.uid, (1, 1, 1))
        return lck
    else:
        lck = hgs.ValueScaleLock(uid=uid, **kwargs)
        for view, track in data:
            assert isinstance(view.uid, str)
            assert isinstance(track.uid, str)
            vtuid = f"{view.uid}.{track.uid}"
            setattr(lck, vtuid, {"track": track.uid, "view": view.uid})
        return lck
