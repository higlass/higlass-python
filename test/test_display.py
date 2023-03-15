from unittest.mock import MagicMock

from higlass._display import HTMLRenderer, RendererRegistry, renderers
import pytest


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


def test_temporary_renderer():
    registry = RendererRegistry()
    mock = MagicMock()

    def renderer(viewconf: dict, **metadata):
        return {
            "text/plain": "some content",
        }

    registry.register("foo", renderer)
    registry.register("mock", mock)

    registry.enable("foo")

    with registry.enable("mock") as render:
        assert registry.active == "mock"
        render({"hello": "world"})

    mock.assert_called_once_with({"hello": "world"})

    render = registry.get()
    mimebundle = render({})
    assert registry.active == "foo"
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
