from higlass.viewer import view
from higlass.viewer import display

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'higlass-jupyter',
        'require': 'higlass-jupyter/extension'
    }]

def _jupyter_labextension_paths():
    return [{
        'name': 'higlass-jupyter',
        'src': 'staticlab'
    }]
