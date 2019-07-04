import logging
import ipywidgets as widgets
from traitlets import Unicode
# from traitlets import default
from traitlets import List
from traitlets import Dict
from traitlets import Int

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
    hg_options = Dict({}).tag(sync=True)
    height = Int().tag(sync=True)

    def __init__(self, **kwargs):
        # self.viewconf = viewconf
        super(HiGlassDisplay, self).__init__(**kwargs)

    # @default('layout')
    # def _default_layout(self):
    #     return widgets.Layout(height='600px', align_self='stretch')

    # def set_data(self, js_data):
    #     self._model_data = js_data


def display(
    views,
    location_syncs=[],
    zoom_syncs=[],
    host='localhost',
    server_port=None,
    log_level=logging.ERROR
):
    '''
    Instantiate a HiGlass display with the given views
    '''
    from .server import Server
    from .client import ViewConf
    tilesets = []

    for view in views:
        for track in view.tracks:
            if track.tracks:
                for track1 in track.tracks:
                    if track1.tileset:
                        tilesets += [track1.tileset]

            if track.tileset:
                tilesets += [track.tileset]

    server = Server(tilesets, host=host, port=server_port)
    server.start(log_level=log_level)

    for view in views:
        for track in view.tracks:
            if track.tracks:
                for track1 in track.tracks:
                    if ('server' not in track1.viewconf or
                            track1.viewconf['server'] is None):
                        track1.viewconf['server'] = server.api_address
            else:
                if ('server' not in track.viewconf or
                        track.viewconf['server'] is None):
                    track.viewconf['server'] = server.api_address

    conf = ViewConf(
        views,
        location_syncs=location_syncs,
        zoom_syncs=zoom_syncs)

    return (HiGlassDisplay(viewconf=conf.to_dict()), server, conf)


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
