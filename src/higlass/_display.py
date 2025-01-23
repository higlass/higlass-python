from __future__ import annotations

import contextlib
import json
import uuid
from dataclasses import dataclass, field
from typing import Protocol

import jinja2

HTML_TEMPLATE = jinja2.Template(
    """
<!DOCTYPE html>
<html>
  <head>
    <script src="https://unpkg.com/requirejs-toggle"></script>
    {% for plugin_url in plugin_urls %}
    <script src="{{ plugin_url }}"></script>
    {% endfor %}
    <script src="https://unpkg.com/requirejs-toggle"></script>
  </head>
  <body>
    <div id="{{ output_div }}"></div>
  </body>
  <script type="module">
    import * as hglib from "https://esm.sh/higlass@{{ higlass_version }}?deps=react@{{ react_version }},react-dom@{{ react_version }},pixi.js@{{ pixijs_version }}";

    let el = document.getElementById('{{ output_div }}');
    hglib.viewer(el, {{ viewconf }});

    // prevent right click events from bubbling up to Jupyter/JupyterLab
    el.addEventListener("contextmenu", (event) => event.stopPropagation());
  </script>
</html>
"""  # noqa
)


def viewconf_to_html(
    viewconf: dict,
    higlass_version: str = "1.13",
    react_version: str = "17",
    pixijs_version: str = "6",
    output_div: str = "vis",
    json_kwds: dict | None = None,
    plugin_urls: list[str] | None = None,
):
    """Embed the viewconf into an HTML template.

    The HTML template includes imports for HiGlass and any specified plugins
    and will display an interactive visualization of the embedded viewconf
    when loaded in the web browser.

    Parameters
    ----------

    viewconf : dict
        The top-level HiGlass viewconf.

    higlass_version : str, optional
        The HiGlass client version.

    react_version : str, optional
        The react and react-dom peer dependency versions.

    pixijs_version : str, optional
        The pixi.js perr dependency version.

    output_div : str, optional
        An id for the div which the visualization renders.

    json_kwds : dict, optional
        Additional arguments to pass to `json.dumps`.

    plugin_urls : list[str], optional
        URLs for plugin tracks or data fetchers to be loaded on the page.
    """
    return HTML_TEMPLATE.render(
        viewconf=json.dumps(viewconf, **(json_kwds or {})),
        higlass_version=higlass_version,
        react_version=react_version,
        pixijs_version=pixijs_version,
        output_div=output_div,
        plugin_urls=plugin_urls or [],
    )


class RendererProtocol(Protocol):
    """A callable that converts a dict viewconf into full mimebundle."""

    def __call__(self, viewconf: dict, **metadata) -> dict:
        """Creates a full mimebundle from a dictionary viewconf.

        Parameters
        ----------

        viewconf : dict
            A top-level HiGlass viewconf (e.g., `hg.Viewconf.dict()`))

        **metadata : dict
            Any extra metadata for the renderer.

        Returns
        -------

        mimebundle : a full mimebundle containing the mapping from all
            mimetypes to data. See return type of `_repr_mimebundle_`
            method in IPython documentation.


        Examples
        --------

        >>> def render_text(viewconf: dict):
        >>>     return {
        >>>         "text/plain": "Viewconf(...)",
        >>>     }

        """
        ...


class BaseRenderer(RendererProtocol):
    def __init__(self, output_div: str = "jupyter-hg-{}", **kwargs):
        self._output_div = output_div
        self.kwargs = kwargs

    @property
    def output_div(self):
        """Creates a unique id for the output div each time it is accessed."""
        return self._output_div.format(uuid.uuid4().hex)

    def __call__(self, viewconf: dict, **metadata):
        raise NotImplementedError()


class HTMLRenderer(BaseRenderer):
    def __call__(self, viewconf: dict, **metadata):
        kwargs = self.kwargs.copy()
        kwargs.update(metadata)
        html = viewconf_to_html(viewconf=viewconf, output_div=self.output_div, **kwargs)
        return {"text/html": html}


@contextlib.contextmanager
def managed_enable(registry: RendererRegistry, reset: str | None):
    """Temporarily enables a renderer.

    Parameters
    ----------
    registry : PluginRegistry
        The plugin registry to potentially reset the active plugin.

    reset : str | None
        The previous name of the active plugin.
    """
    try:
        yield registry.get()
    finally:
        registry.active = reset


@dataclass
class RendererRegistry:
    """A registery for multiple HiGlass renderers.

    Allows for multiple renders to be registered, and dynamically enabled/disabled
    for the viewconf.

    Examples
    --------

    >>> import higlass as hg
    >>> hg.renderers.register("my-renderer", MyRenderer())
    >>> hg.renderers.enable("my-renderer")
    >>> hg.view(hg.track("heatmap")) # calls the custom renderer

    """

    renderers: dict[str, RendererProtocol] = field(default_factory=dict)
    active: str | None = None

    def register(self, name: str, renderer: RendererProtocol):
        """Reigster a custom renderer.

        Parameters
        ----------

        name : str
            A uniquely identifiable name.

        renderer : RendererProtocol
            A Callable that implements the RendererProtocol.
        """
        self.renderers[name] = renderer

    def enable(self, name: str):
        """Examples a previously registered renderer.

        Parameters
        ----------

        name : str
            The name of a previously registered renderer.
        """
        if name not in self.renderers:
            raise ValueError(f"Renderer '{name}' has not been registered.")
        prev = self.active
        self.active = name
        return managed_enable(self, prev)

    def get(self):
        """Get the enabled renderer."""
        if self.active is None:
            raise ValueError("No renderer enabled.")
        return self.renderers[self.active]


html_renderer = HTMLRenderer()

renderers = RendererRegistry()
renderers.register("default", html_renderer)
renderers.register("html", html_renderer)
renderers.enable("default")
