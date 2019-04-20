from .widgets import HiGlassDisplay


def display(views, location_sync=[], zoom_sync=[], host='localhost', server_port=None):
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
    print("tilesets:", tilesets)

    server = Server(tilesets, host=host, port=server_port)
    server.start()

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


    conf = ViewConf(views, location_syncs=location_syncs,
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
        if (ts.track_type is not None
                and ts.track_position is not None):
            curr_view.add_track(ts.track_type,
                    ts.track_position,
                    api_url=server.api_address,
                    tileset_uuid=ts.uuid,
                )

    curr_view.server = server
    return curr_view
