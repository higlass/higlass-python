import logging
import ipywidgets as widgets
from traitlets import (
    Bool,
    Dict,
    Float,
    Int,
    List,
    Unicode,
    Union,
)

from ._version import __version__


@widgets.register
class HiGlassDisplay(widgets.DOMWidget):
    _view_name = Unicode("HiGlassDisplayView").tag(sync=True)
    _model_name = Unicode("HiGlassDisplayModel").tag(sync=True)
    _view_module = Unicode("higlass-jupyter").tag(sync=True)
    _model_module = Unicode("higlass-jupyter").tag(sync=True)
    _view_module_version = Unicode(__version__).tag(sync=True)
    _model_module_version = Unicode(__version__).tag(sync=True)
    _model_data = List([]).tag(sync=True)

    viewconf = Dict({}).tag(sync=True)
    height = Int().tag(sync=True)

    dom_element_id = Unicode(read_only=True).tag(sync=True)

    # Read-only properties that get updated by HiGlass exclusively
    location = List(Union([Float(), List()]), read_only=True).tag(sync=True)
    cursor_location = List([], read_only=True).tag(sync=True)
    selection = List([], read_only=True).tag(sync=True)

    # Short-hand options
    auth_token = Unicode().tag(sync=True)
    bounded = Bool(None, allow_none=True).tag(sync=True)
    default_track_options = Dict({}).tag(sync=True)
    dark_mode = Bool(False).tag(sync=True)
    renderer = Unicode().tag(sync=True)
    select_mode = Bool(False).tag(sync=True)
    selection_on_alt = Bool(False).tag(sync=True)
    # For any kind of options. Note that whatever is defined in options will
    # be overwritten by the short-hand options
    options = Dict({}).tag(sync=True)

    def __init__(self, **kwargs):
        super(HiGlassDisplay, self).__init__(**kwargs)


def display(
    views,
    location_syncs=[],
    zoom_syncs=[],
    overlays=[],
    host='localhost',
    server_port=None,
    dark_mode=False,
    log_level=logging.ERROR
):
    '''
    Instantiate a HiGlass display with the given views
    '''
    from .server import Server
    from .client import CombinedTrack, View, ViewConf
    tilesets = []

    for view in views:
        for track in view.tracks:
            if hasattr(track, 'tracks'):
                for track1 in track.tracks:
                    if track1.tileset:
                        tilesets += [track1.tileset]

            if track.tileset:
                tilesets += [track.tileset]

    server = Server(tilesets, host=host, port=server_port)
    server.start(log_level=log_level)

    cloned_views = [View.from_dict(view.to_dict()) for view in views]

    for view in cloned_views:
        for track in view.tracks:
            if isinstance(track, CombinedTrack):
                for track1 in track.tracks:
                    if ('server' not in track1.conf or
                            track1.conf['server'] is None):
                        track1.conf['server'] = server.api_address
            else:
                if ('server' not in track.conf or
                        track.conf['server'] is None):
                    track.conf['server'] = server.api_address

    viewconf = ViewConf(
        cloned_views,
        location_syncs=location_syncs,
        zoom_syncs=zoom_syncs,
        overlays=overlays)

    return (
        HiGlassDisplay(
            viewconf=viewconf.to_dict(),
            hg_options={
                'theme': 'dark' if dark_mode else 'light'
            }
        ),
        server,
        viewconf
    )


def view(tilesets):
    '''
    Create a higlass viewer that displays the specified tilesets

    Parameters:
    -----------

    Returns
    -------
        Nothing
    '''
    from .server import Server
    from .client import View

    curr_view = View()
    server = Server()
    server.start(tilesets)

    for ts in tilesets:
        if ts.track_type is not None and ts.track_position is not None:
            curr_view.add_track(
                ts.track_type,
                ts.track_position,
                api_url=server.api_address,
                tileset_uuid=ts.uuid,
            )

    curr_view.server = server
    return curr_view
