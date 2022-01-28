from .model import *
from .display import renderers

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
