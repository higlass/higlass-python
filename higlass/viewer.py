import higlass.server as hgse
import higlass.client as hgc

from .widgets import HiGlassDisplay

def display(views, location_sync=[], zoom_sync=[]):
    '''
    Instantiate a HiGlass display with the given views
    '''
    tilesets = []

    for view in views:
        for track in view.tracks:
            if track.tileset:
                tilesets += [track.tileset]

    server = hgse.Server(tilesets)
    server.start()

    for view in views:
        for track in view.tracks:
            track.viewconf['server'] = server.api_address

    conf = hgc.ViewConf(views, location_sync=location_sync, zoom_sync=zoom_sync)

    return (server, HiGlassDisplay(viewconf=conf.to_json()))

def view(tilesets):
    '''
    Create a higlass viewer that displays the specified tilesets

    Parameters:
    -----------

    Returns
    -------
        Nothing
    '''
    curr_view = hgc.View()
    server = hgse.start(
                tilesets
            )

    for ts in tilesets:
        if (ts.track_type is not None
                and ts.track_position is not None):
            curr_view.add_track(ts.track_type,
                    ts.track_position,
                    api_url=server.api_address,
                    tileset_uuid=ts.uuid,
                )


    curr_view.server = server
    return curr_view
