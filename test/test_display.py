import pytest
from higlass._display import HTMLRenderer, RendererRegistry, renderers


def test_registry():
    registery = RendererRegistry()

    with pytest.raises(ValueError):
        registery.get()

    def renderer(viewconf: dict, **metadata):
        return {
            "text/plain": "some content",
        }

    registery.register("foo", renderer)

    with pytest.raises(ValueError):
        registery.get()

    with pytest.raises(ValueError):
        registery.enable("blah")

    registery.enable("foo")

    render = registery.get()

    mimebundle = render({})

    assert isinstance(mimebundle, dict)
    assert mimebundle["text/plain"] == "some content"


def test_html_renderer():
    """Just a smoke test to make sure our html gets a unique ID"""

    default_renderer = renderers.get()
    assert isinstance(default_renderer, HTMLRenderer)

    mimebundle = default_renderer(
        {
            "foo": "bar",
        }
    )

    assert "text/html" in mimebundle
    assert 'id="jupyter-hg-' in mimebundle["text/html"]
    assert '"foo": "bar"' in mimebundle["text/html"]
