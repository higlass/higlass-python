import logging
from higlass_widget import HiGlassWidget as HiGlassDisplay

from ._version import __version__

def display(
    views,
    location_syncs=[],
    value_scale_syncs=[],
    zoom_syncs=[],
    host="localhost",
    server_port=None,
    dark_mode=False,
    log_level=logging.ERROR,
    fuse=True,
    auth_token=None,
    proxy_base=None,
):
    """
    Instantiate a HiGlass display with the given views.

    Args:
        views: A list of views to display. If the items in the list are
            lists themselves, then automatically create views out of them.
        location_syncs: A list of lists, each containing a list of views which
            will scroll together.
        value_scale_syncs: A list containing the value scale syncs. Each sync can be
            one of:
                1. a list of (View, Track) tuples
                2. a list of Tracks (assumes that there is only one view)
                3. a list of strings of the form "{viewUid}.{trackUid}"
        zoom_syncs: A list of lists, each containing a list of views that
            will zoom together.
        host: The host on which the internal higlass server will be running on.
        server_port: The port on which the internal higlass server will be running on.
        dark_mode: Whether to use dark mode or not.
        log_level: Level of logging to perform.
        fuse: Whether to mount the fuse filesystem. Set to False if not loading any
            data over http or https.
        proxy_base: Url and base path of server to use as proxy for the client

    Returns:
        (display: HiGlassDisplay, server: higlass.server.Server, higlass.client.viewconf) tuple
        Display is an object used to create
        a HiGlass viewer within a Jupyter notebook. The server object encapsulates
        a Flask instance of a higlass server and the viewconf is a Python object
        containing the viewconf describing the higlass dashboard.
    """
    from .server import Server
    from .client import CombinedTrack, DividedTrack, View, ViewConf, ViewportProjection

    tilesets = []

    # views can also be passed in as lists of tracks
    new_views = []
    for view in views:
        if isinstance(view, (tuple, list)):
            # view is a list of tracks
            new_views.append(View(view))
        else:
            new_views.append(view)
    views = new_views

    for view in views:
        for track in view.tracks:
            if hasattr(track, "tracks"):
                for track1 in track.tracks:
                    if not isinstance(track1, ViewportProjection) and track1.tileset:
                        tilesets += [track1.tileset]

            if track.tileset:
                tilesets += [track.tileset]

    server = Server(
        tilesets,
        host=host,
        port=server_port,
        fuse=fuse,
        log_level=log_level,
        root_api_address=proxy_base,
    )
    server.start()

    cloned_views = [View.from_dict(view.to_dict()) for view in views]

    for view in cloned_views:
        for track in view.tracks:
            if isinstance(track, CombinedTrack):
                for track1 in track.tracks:
                    if "fromViewUid" in track1.conf:
                        # this is a viewport projection and doesn't have
                        # a server
                        pass
                    elif "server" not in track1.conf or track1.conf["server"] is None:
                        track1.conf["server"] = server.api_address
            elif "fromViewUid" in track.conf:
                pass
            elif "data" in track.conf:
                # probably a divided track with a custom
                # data fetcher
                pass
            else:
                if "server" not in track.conf or track.conf["server"] is None:
                    track.conf["server"] = server.api_address

    viewconf = ViewConf(
        cloned_views,
        location_syncs=location_syncs,
        value_scale_syncs=value_scale_syncs,
        zoom_syncs=zoom_syncs,
    )

    extra_args = {}
    if auth_token:
        extra_args["auth_token"] = auth_token

    return (
        HiGlassDisplay(
            viewconf=viewconf.to_dict(),
            hg_options={
                "theme": "dark" if dark_mode else "light",
            },
            **extra_args
        ),
        server,
        viewconf,
    )
