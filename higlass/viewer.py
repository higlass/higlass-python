import logging
import ipywidgets as widgets
from itertools import chain
from traitlets import (
    Unicode,
    Bool,
    Int,
    Dict,
    List,
    All,
    parse_notifier_name
)

from ._version import __version__


class _EventHandlers(object):

    def __init__(self):
        self._listeners = {}

    def on(self, names, handler):
        names = parse_notifier_name(names)
        for n in names:
            self._listeners.setdefault(n, []).append(handler)

    def off(self, names, handler):
        names = parse_notifier_name(names)
        for n in names:
            try:
                if handler is None:
                    del self._listeners[n]
                else:
                    self._listeners[n].remove(handler)
            except KeyError:
                pass

    def notify_listeners(self, event, widget):
        event_listeners = self._listeners.get(event['type'], [])
        all_listeners = self._listeners.get(All, [])
        for listener in chain(event_listeners, all_listeners):
            listener(event, widget)


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
    select_mode = Bool(False).tag(sync=True)

    def __init__(self, **kwargs):
        self._initialized = False
        super(HiGlassDisplay, self).__init__(**kwargs)
        self._handlers = _EventHandlers()
        self.on_msg(self._handle_higlass_msg)
        self._initialized = True

    def _handle_higlass_msg(self, widget, content, buffers=None):
        try:
            self._handle_higlass_msg_content(content)
        except Exception as e:
            self.log.error(e)
            self.log.exception("Unhandled exception while handling msg")

    def _handle_higlass_msg_content(self, data):
        """Handle incoming messages from the HiGlass view"""
        if not self._initialized or 'type' not in data:
            return

        self._handlers.notify_listeners(data, self)

    def on(self, names, handler):
        """
        Setup a handler to be called when a user interacts with the current
        instance.
        Parameters
        ----------
        names : list, str, All
            If names is All, the handler will apply to all events.  If a list
            of str, handler will apply to all events named in the list.  If a
            str, the handler will apply just the event with that name.
        handler : callable
            A callable that is called when the event occurs. Its
            signature should be ``handler(event, widget)``, where
            ``event`` is a dictionary and ``widget`` is the HiGlass widget
            instance that fired the event. The ``event`` dictionary at least
            holds a ``name`` key which specifies the name of the event that
            occurred.
        Notes
        -----
        Here's the list of events that you can listen to on QgridWidget
        instances via the ``on`` method::
            [
                'location',
                'cursor_location',
                'selection',
            ]
        For details about the events please see
        https://docs.higlass.io/javascript_api.html#public.on
        """
        self._handlers.on(names, handler)

    def off(self, names, handler):
        """
        Remove an event handler that was registered with the current
        instance's ``on`` method.
        Parameters
        ----------
        names : list, str, All (default: All)
            The names of the events for which the specified handler should be
            uninstalled. If names is All, the specified handler is uninstalled
            from the list of notifiers corresponding to all events.
        handler : callable
            A callable that was previously registered with the current
            instance's ``on`` method.
        """
        self._handlers.off(names, handler)


def display(
    views,
    location_syncs=[],
    zoom_syncs=[],
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
        zoom_syncs=zoom_syncs)

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
