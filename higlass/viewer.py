from higlass_jupyter import HiGlassDisplay
import higlass.server as hgse

def viewer(tracks):
    '''
    Create a higlass viewer that displays the specified tilesets

    Parameters:
    -----------

    Returns 
    -------
        Nothing
    '''
    server = hgse.start(tilesets=[tilesets])

    pass      
