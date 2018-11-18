from higlass.viewer import view
from higlass.viewer import display

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'higlass',
        'require': 'higlass/extension'
    }]
