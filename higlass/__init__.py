from higlass.viewer import view, display

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'higlass-jupyter',
        'require': 'higlass-jupyter/extension'
    }]

from ._version import __version__
