import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import jinja2

HTML_TEMPLATE = jinja2.Template(
    """
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="https://esm.sh/higlass@{{ higlass_version }}/dist/hglib.css">
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
    import hglib from "https://esm.sh/higlass@{{ higlass_version }}?deps=react@{{ react_version }},react-dom@{{ react_version }},pixi.js@{{ pixijs_version }}";
    hglib.viewer(
      document.getElementById('{{ output_div }}'),
      JSON.parse({{ spec }}),
    );
    </script>
</html>
"""  # noqa
)


def spec_to_html(
    spec: Dict[str, Any],
    higlass_version: str = "1.11",
    react_version: str = "17",
    pixijs_version: str = "6",
    output_div: str = "vis",
    json_kwds: Optional[Dict[str, Any]] = None,
    plugin_urls: Optional[List[str]] = None,
):
    json_kwds = json_kwds or {}
    plugin_urls = plugin_urls or []

    return HTML_TEMPLATE.render(
        spec=json.dumps(spec, **json_kwds),
        higlass_version=higlass_version,
        react_version=react_version,
        pixijs_version=pixijs_version,
        output_div=output_div,
        plugin_urls=plugin_urls,
    )


class BaseRenderer:
    def __init__(self, output_div: str = "jupyter-hg-{}", **kwargs):
        self._output_div = output_div
        self.kwargs = kwargs

    @property
    def output_div(self):
        return self._output_div.format(uuid.uuid4().hex)

    def __call__(self, spec, **metadata):
        raise NotImplementedError()


class HTMLRenderer(BaseRenderer):
    def __call__(self, spec, **metadata):
        kwargs = self.kwargs.copy()
        kwargs.update(metadata)
        html = spec_to_html(spec=spec, output_div=self.output_div, **kwargs)
        return {"text/html": html}


@dataclass
class RendererRegistry:
    renderers: Dict[str, BaseRenderer] = field(default_factory=dict)
    active: Optional[str] = None

    def register(self, name: str, renderer: BaseRenderer):
        self.renderers[name] = renderer

    def enable(self, name: str):
        assert name in self.renderers
        self.active = name

    def get(self):
        assert isinstance(self.active, str) and self.active in self.renderers
        return self.renderers[self.active]


html_renderer = HTMLRenderer()

renderers = RendererRegistry()
renderers.register("default", html_renderer)
renderers.register("html", html_renderer)
renderers.register("colab", html_renderer)
renderers.register("kaggle", html_renderer)
renderers.register("zeppelin", html_renderer)
renderers.enable("default")
