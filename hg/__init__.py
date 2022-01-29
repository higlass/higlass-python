from .model import *
from .display import renderers
from .mixins import _TrackTypeMixen

class Config(HiglassViewconf):

    def __rich_repr__(self):
        return self.__iter__()

    def _repr_mimebundle_(self, include=None, exclude=None):
        renderer = renderers.get()
        return renderer(self.json()) if renderer else {}

    def display(self):
        """Render top-level chart using IPython.display."""
        from IPython.display import display

        display(self)

class Track(EnumTrack, _TrackTypeMixen):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            type=kwargs.pop('type', 'horizontal-gene-annotations'),
            **kwargs
        )

    def view(self, **kwargs):
        copy = self.copy()
        for key, val in kwargs.items():
            setattr(copy, key, val)
        return Config(
            views=[
                View(
                    tracks={ "top": [copy] },
                    layout=Layout(w=1, h=1, x=1, y=1)     
                )
            ]
        )
