import json
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

import jinja2

HTML_TEMPLATE = jinja2.Template(
    """
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <link rel="stylesheet" href="{{ base_url }}/higlass@{{ higlass_version }}/dist/hglib.css">
</head>
<body>
  <div id="{{ output_div }}"></div>
  <script type="module">

    async function loadScript(src) {
        return new Promise(resolve => {
            const script = document.createElement('script');
            script.onload = resolve;
            script.src = src;
            script.async = false;
            document.head.appendChild(script);
        });
    }

    async function loadHiglass() {
        // Manually load scripts from window namespace since requirejs might not be
        // available in all browser environments.
        // https://github.com/DanielHreben/requirejs-toggle
        if (!window.hglib) {
            window.__requirejsToggleBackup = {
                define: window.define,
                require: window.require,
                requirejs: window.requirejs,
            };
            for (const field of Object.keys(window.__requirejsToggleBackup)) {
                window[field] = undefined;
            }

            // load dependencies sequentially
            const sources = [
                "{{ base_url }}/react@{{ react_version }}/umd/react.production.min.js",
                "{{ base_url }}/react-dom@{{ react_version }}/umd/react-dom.production.min.js",
                "{{ base_url }}/pixi.js@{{ pixijs_version }}/dist/browser/pixi.min.js",
                "https://unpkg.com/react-bootstrap@0.32.1/dist/react-bootstrap.min.js",
                "{{ base_url }}/higlass@{{ higlass_version }}/dist/hglib.js",
                {% for plugin_url in plugin_urls %}"{{ plugin_url }}",{% endfor %}
            ];

            for (const src of sources) await loadScript(src);

            // restore requirejs after scripts have loaded
            Object.assign(window, window.__requirejsToggleBackup);
            delete window.__requirejsToggleBackup;
        }
        return window.hglib;
    };

    var el = document.getElementById('{{ output_div }}');
    var spec = JSON.parse({{ spec }});

    loadHiglass().then(hglib => {
        hglib.viewer(el, spec);
    })
  </script>
</body>
</html>
"""
)


def spec_to_html(
    spec,
    higlass_version="1.11",
    react_version="17",
    pixijs_version="6",
    base_url="https://unpkg.com",
    output_div="vis",
    embed_options=None,
    json_kwds=None,
    plugin_urls=[],
):
    embed_options = embed_options or dict(padding=0)
    json_kwds = json_kwds or {}

    return HTML_TEMPLATE.render(
        spec=json.dumps(spec, **json_kwds),
        embed_options=json.dumps(embed_options, **json_kwds),
        higlass_version=higlass_version,
        react_version=react_version,
        pixijs_version=pixijs_version,
        base_url=base_url,
        output_div=output_div,
        plugin_urls=plugin_urls,
    )


class BaseRenderer:
    def __init__(self, output_div="jupyter-hg-{}", **kwargs):
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
