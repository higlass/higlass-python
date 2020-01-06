import logging
import ipywidgets as widgets
from traitlets import Bool, Dict, Float, Int, List, Unicode, Union
from IPython.display import display as ipy_display

from ._version import __version__


@widgets.register
class HiGlassDisplay(widgets.DOMWidget):
    print("yoo")
    _view_name = Unicode("HiGlassDisplayView").tag(sync=True)
    _model_name = Unicode("HiGlassDisplayModel").tag(sync=True)
    _view_module = Unicode("higlass-jupyter").tag(sync=True)
    _model_module = Unicode("higlass-jupyter").tag(sync=True)
    _view_module_version = Unicode(__version__).tag(sync=True)
    _model_module_version = Unicode(__version__).tag(sync=True)
    _model_data = List([]).tag(sync=True)

    viewconf = Dict({}).tag(sync=True)
    height = Int().tag(sync=True)

    dom_element_id = Unicode(read_only=True).tag(sync=True)

    # Read-only properties that get updated by HiGlass exclusively
    location = List(Union([Float(), List()]), read_only=True).tag(sync=True)
    cursor_location = List([], read_only=True).tag(sync=True)
    selection = List([], read_only=True).tag(sync=True)

    # Short-hand options
    auth_token = Unicode().tag(sync=True)
    bounded = Bool(None, allow_none=True).tag(sync=True)
    default_track_options = Dict({}).tag(sync=True)
    dark_mode = Bool(False).tag(sync=True)
    renderer = Unicode().tag(sync=True)
    select_mode = Bool(False).tag(sync=True)
    selection_on_alt = Bool(False).tag(sync=True)
    # For any kind of options. Note that whatever is defined in options will
    # be overwritten by the short-hand options
    options = Dict({}).tag(sync=True)

    def __init__(self, **kwargs):
        super(HiGlassDisplay, self).__init__(**kwargs)

    def _handle_message(self, object, content, buffers):
        # Every content has a "type".
        print("handle message")

    def _ipython_display_(self, **kwargs):
        """Called when `IPython.display.display` is called on the widget."""
        print("expanse")
        plaintext = repr(self)
        if len(plaintext) > 110:
            plaintext = plaintext[:110] + "…"
        data = {
            "text/plain": plaintext,
            "image/png": "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAEumlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNS41LjAiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6ZXhpZj0iaHR0cDovL25zLmFkb2JlLmNvbS9leGlmLzEuMC8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgZXhpZjpQaXhlbFhEaW1lbnNpb249IjMyIgogICBleGlmOlBpeGVsWURpbWVuc2lvbj0iMzIiCiAgIGV4aWY6Q29sb3JTcGFjZT0iMSIKICAgdGlmZjpJbWFnZVdpZHRoPSIzMiIKICAgdGlmZjpJbWFnZUxlbmd0aD0iMzIiCiAgIHRpZmY6UmVzb2x1dGlvblVuaXQ9IjIiCiAgIHRpZmY6WFJlc29sdXRpb249Ijk2LjAiCiAgIHRpZmY6WVJlc29sdXRpb249Ijk2LjAiCiAgIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiCiAgIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIKICAgeG1wOk1vZGlmeURhdGU9IjIwMTktMTItMzFUMTc6MTQ6MjktMDg6MDAiCiAgIHhtcDpNZXRhZGF0YURhdGU9IjIwMTktMTItMzFUMTc6MTQ6MjktMDg6MDAiPgogICA8eG1wTU06SGlzdG9yeT4KICAgIDxyZGY6U2VxPgogICAgIDxyZGY6bGkKICAgICAgc3RFdnQ6YWN0aW9uPSJwcm9kdWNlZCIKICAgICAgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWZmaW5pdHkgRGVzaWduZXIgKFNlcCAyMiAyMDE5KSIKICAgICAgc3RFdnQ6d2hlbj0iMjAxOS0xMi0zMVQxNzoxNDoyOS0wODowMCIvPgogICAgPC9yZGY6U2VxPgogICA8L3htcE1NOkhpc3Rvcnk+CiAgPC9yZGY6RGVzY3JpcHRpb24+CiA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSJyIj8+AuOqXgAAAYFpQ0NQc1JHQiBJRUM2MTk2Ni0yLjEAACiRdZHfK4NRGMc/NiKmKcKFsoSrTUyJG2USamnNlOFme/dLbfP2vltabpXbFSVu/LrgL+BWuVaKSMmNG9fEDev1vNtqkp3TeZ7P+Z7neTrnOWAJJJWUXjsIqXRG8097HIvBJUf9Cza6aRfbEVJ0dcLn81J1fN5TY/pbl1mrety/oykS1RWoaRAeV1QtIzwj7F3PqCbvCLcpiVBE+EzYqckFhe9MPVziV5PjJf42WQv4J8HSIuyI/+LwL1YSWkpYXk5vKplVyvcxX2KLphfmxffI6kLHzzQeHMwyxSQjDDEmdgQXbgZkR5X8wWL+HGuSq4hVyaGxSpwEGZyiZqV6VHxM9KjMJDmz/3/7qseG3aXqNg/UPRvGex/Ub0MhbxhfR4ZROAbrE1ymK/lrhzD6IXq+ovUegH0Tzq8qWngXLrag81ENaaGiZJVlicXg7RSag9B6A43LpZ6Vzzl5gMCGfNU17O1Dv8TbV34ATaNn2k0+yt8AAAAJcEhZcwAADsQAAA7EAZUrDhsAAAOkSURBVFiFvZdraBxVFMd/987MPrJmTWwtTWJtlU1okxhF6BZtBCNMIFZaFPFDlIhPkIYiARGqVlBSigEDoiAIsREsqLRiXCl0xYIV1KnSWmrS0GBiapJiMS1tTLLZzYwf9kGymdnNzAbPt5l7zvn/OPd1rsCDtRwebDhzZeGLxKK1SUBKCi4DU5oUFyoDMtZ6e+Dkh3vq5laTS3gBAIi8f6517Hrqy5RJWf6YX+FaSJNH6m/RDv7wbMOEJwDdsFTgYeDreFRYbiEANMmNCr/sva/Kf2igfZttRaSDeCUQA74C3tYNyxZ0pLPpxJaw+qgqmbUbT5qUX5kzD5y8NB+PfnS+2s5nRWLdsLYCA0Dtkt/dwBteKwEQUMSfW8LKngt7m35zBNAN61bgLGBHuyYQjeu0nb+82JhbF7kp0A1LAv0O4gCv4WE6pABFkAKYX7Q2D19Nfrb7yFBwBQDQBbQ50XuBkAKqQ0pnQBGXsz43ktbOn6YSry4D0A2rGjhYRNwVhE8yUx1SOv96+e4P8n2uJsyu5r7fa3IAwHOAtkqAVUE8tClYbycO6d0xOJ3cDyAy+30UuM0FQNYKLsyshQ6dufRvylqW369wbd894SpJ+rDxIg5FKlHIEotUHBuZbZHAAx7FS4aYnjcfkcCdJQIA7AfudRuUNK2tErijRHELeD4eFb96iK1Sca6ACRS+Ui0TXzLx+ubpiVjtwMUNTm6fDM3Y3jmmxUYVUB3iTsWj4kGnpB1Hh7VvRucO/zNv9gK9BUGdzZTApNuojqPDWiwt3u5RGAAhGPUEcGoi8dR0ieIAqmBMAkNuAx+vLevfEJS2p5wbU6QYk6TvflfW0xYxn66/aV+pEOWa+FEC3wEz/zdEUBXjT9SFYjIeFQngUydH3bAU3bDq1hoipIq+nrbIQnZ/voXNntcNSwH6gNO6Ye1YKwhFkKxfp30Mmes4HhWTwLv5fhnxDiAMnFgriPVB+eb3zzSM5wAy1g0YS76bM+JZWxOIsE8c776/8p3sd35TWgWcBmoK5LgOtMaj4me7wVeOj8j+wZn3/p4z9+aPBRQx2bRe22680Jg7e5ad0fGomCLdHxR6zXiqRFAVFyMV6q6l4isAMhDngO0sn46SIG72iW93bPQ1n3/prrP5voWeZkHS93wXOPb6Rafj2Mhs+2ORss972iILdj5Fu5jMujgAPAmUu4UoZqtuo3TD8gMtwG5gG+kHTE0mxx/ArnhUjLsF+A/qg322q+VaHAAAAABJRU5ErkJggg==",
        }
        if self._view_name is not None:
            # The 'application/vnd.jupyter.widget-view+json' mimetype has not been registered yet.
            # See the registration process and naming convention at
            # http://tools.ietf.org/html/rfc6838
            # and the currently registered mimetypes at
            # http://www.iana.org/assignments/media-types/media-types.xhtml.
            data["application/vnd.jupyter.widget-view+json"] = {
                "version_major": 2,
                "version_minor": 0,
                "model_id": self._model_id,
            }
        ipy_display(data, raw=True)

        if self._view_name is not None:
            self._handle_displayed(**kwargs)


def display(
    views,
    location_syncs=[],
    value_scale_syncs=[],
    zoom_syncs=[],
    host="localhost",
    server_port=None,
    dark_mode=False,
    log_level=logging.ERROR,
    no_fuse=False,
):
    """
    Instantiate a HiGlass display with the given views
    """
    from .server import Server
    from .client import CombinedTrack, View, ViewConf, ViewportProjection

    tilesets = []

    for view in views:
        for track in view.tracks:
            if hasattr(track, "tracks"):
                for track1 in track.tracks:
                    if not isinstance(track1, ViewportProjection) and track1.tileset:
                        tilesets += [track1.tileset]

            if track.tileset:
                tilesets += [track.tileset]

    server = Server(tilesets, host=host, port=server_port, no_fuse=no_fuse)
    server.start(log_level=log_level)

    cloned_views = [View.from_dict(view.to_dict()) for view in views]

    for view in cloned_views:
        for track in view.tracks:
            if isinstance(track, CombinedTrack):
                for track1 in track.tracks:
                    if "fromViewUid" in track1.conf:
                        # this is a viewport projection and doesn't have
                        # a server
                        pass
                    elif "server" not in track1.conf or track1.conf["server"] is None:
                        track1.conf["server"] = server.api_address
            elif "fromViewUid" in track.conf:
                pass
            else:
                if "server" not in track.conf or track.conf["server"] is None:
                    track.conf["server"] = server.api_address

    viewconf = ViewConf(
        cloned_views,
        location_syncs=location_syncs,
        value_scale_syncs=value_scale_syncs,
        zoom_syncs=zoom_syncs,
    )

    return (
        HiGlassDisplay(
            viewconf=viewconf.to_dict(),
            hg_options={"theme": "dark" if dark_mode else "light"},
        ),
        server,
        viewconf,
    )
