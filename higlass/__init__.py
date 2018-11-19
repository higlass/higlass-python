from higlass.viewer import view, display

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-higlass',
        'require': 'jupyter-higlass/extension'
    }]
