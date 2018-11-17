from higlass_jupyter import HiGlassDisplay
import higlass.server as hgse
import higlass.client as hgc

def viewer(tilesets):
    '''
    Create a higlass viewer that displays the specified tilesets

    Parameters:
    -----------

    Returns 
    -------
        Nothing
    '''
    view = hgc.View()
    
    server = hgse.start(
                tilesets
            )

    for ts in tilesets:
        if (ts.track_type is not None 
                and ts.position is not None):
            view.add_track(track.track_type,
                    track.position,
                    api_url=server.server.api_address
                )

    return view
