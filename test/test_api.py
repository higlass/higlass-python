from __future__ import annotations

from typing import ClassVar, Literal

import pytest

import higlass as hg


@pytest.mark.parametrize(
    "args,expected",
    [
        ("horizontal-line", hg.EnumTrack),
        ("multivec", hg.EnumTrack),
        ("1d-heatmap", hg.EnumTrack),
        ("line", hg.EnumTrack),
        ("point", hg.EnumTrack),
        ("bar", hg.EnumTrack),
        ("divergent-bar", hg.EnumTrack),
        ("stacked-interval", hg.EnumTrack),
        ("gene-annotations", hg.EnumTrack),
        ("linear-2d-rectangle-domains", hg.EnumTrack),
        ("chromosome-labels", hg.EnumTrack),
        ("linear-heatmap", hg.EnumTrack),
        ("1d-value-interval", hg.EnumTrack),
        ("2d-annotations", hg.EnumTrack),
        ("2d-chromosome-annotations", hg.EnumTrack),
        ("2d-chromosome-grid", hg.EnumTrack),
        ("2d-chromosome-labels", hg.EnumTrack),
        ("2d-rectangle-domains", hg.EnumTrack),
        ("2d-tiles", hg.EnumTrack),
        ("arrowhead-domains", hg.EnumTrack),
        ("bedlike", hg.EnumTrack),
        ("cross-rule", hg.EnumTrack),
        ("dummy", hg.EnumTrack),
        ("horizontal-1d-annotations", hg.EnumTrack),
        ("horizontal-1d-heatmap", hg.EnumTrack),
        ("horizontal-1d-tiles", hg.EnumTrack),
        ("horizontal-1d-value-interval", hg.EnumTrack),
        ("horizontal-2d-rectangle-domains", hg.EnumTrack),
        ("horizontal-bar", hg.EnumTrack),
        ("horizontal-chromosome-grid", hg.EnumTrack),
        ("horizontal-chromosome-labels", hg.EnumTrack),
        ("horizontal-divergent-bar", hg.EnumTrack),
        ("horizontal-gene-annotations", hg.EnumTrack),
        ("horizontal-heatmap", hg.EnumTrack),
        ("horizontal-line", hg.EnumTrack),
        ("horizontal-multivec", hg.EnumTrack),
        ("horizontal-point", hg.EnumTrack),
        ("horizontal-rule", hg.EnumTrack),
        ("horizontal-vector-heatmap", hg.EnumTrack),
        ("image-tiles", hg.EnumTrack),
        ("left-axis", hg.EnumTrack),
        ("left-stacked-interval", hg.EnumTrack),
        ("mapbox-tiles", hg.EnumTrack),
        ("osm-2d-tile-ids", hg.EnumTrack),
        ("osm-tiles", hg.EnumTrack),
        ("raster-tiles", hg.EnumTrack),
        ("simple-svg", hg.EnumTrack),
        ("square-markers", hg.EnumTrack),
        ("top-axis", hg.EnumTrack),
        ("top-stacked-interval", hg.EnumTrack),
        ("vertical-1d-annotations", hg.EnumTrack),
        ("vertical-1d-heatmap", hg.EnumTrack),
        ("vertical-1d-tiles", hg.EnumTrack),
        ("vertical-1d-value-interval", hg.EnumTrack),
        ("vertical-2d-rectangle-domains", hg.EnumTrack),
        ("vertical-bar", hg.EnumTrack),
        ("vertical-bedlike", hg.EnumTrack),
        ("vertical-chromosome-grid", hg.EnumTrack),
        ("vertical-chromosome-labels", hg.EnumTrack),
        ("vertical-gene-annotations", hg.EnumTrack),
        ("vertical-heatmap", hg.EnumTrack),
        ("vertical-line", hg.EnumTrack),
        ("vertical-multivec", hg.EnumTrack),
        ("vertical-point", hg.EnumTrack),
        ("vertical-rule", hg.EnumTrack),
        ("vertical-vector-heatmap", hg.EnumTrack),
        ("heatmap", hg.HeatmapTrack),
        ("viewport-projection-center", hg.IndependentViewportProjectionTrack),
        ("combined", hg.PluginTrack),
        (("combined", {"contents": []}), hg.CombinedTrack),
        ("blaaaah", hg.PluginTrack),
    ],
)
def test_creates_correct_track(args: str | tuple, expected: hg.Track):
    track_type, kwargs = (args, {}) if isinstance(args, str) else args
    track = hg.track(track_type, **kwargs)
    assert isinstance(track, expected)  # type: ignore
    assert track.type == track_type


def test_viewport_projection():
    v1 = hg.view(hg.track("heatmap"))
    v2 = hg.view(hg.track("heatmap"))

    v3 = v1.project(v2, on="top")
    assert v3.tracks.top and v3.tracks.top[0].type == "viewport-projection-horizontal"

    v4 = v2.project(v1, on="center", inplace=True)
    assert v2 == v4
    assert v2.tracks.center and v2.tracks.center[1].type == "viewport-projection-center"


def test_hconcat_views():
    v1 = hg.view(hg.track("heatmap"), width=4, height=4)
    v2 = hg.view(hg.track("heatmap"), width=5, height=4)

    viewconf = hg.hconcat(v1, v2)
    assert isinstance(viewconf, hg.Viewconf)
    assert viewconf.views and len(viewconf.views) == 2
    assert viewconf.views[0].layout.x == 0
    assert viewconf.views[0].layout.y == 0
    assert viewconf.views[1].layout.x == 4
    assert viewconf.views[1].layout.y == 0


def test_vconcat_views():
    v1 = hg.view(hg.track("heatmap"), width=4, height=4)
    v2 = hg.view(hg.track("heatmap"), width=5, height=4)

    viewconf = hg.vconcat(v1, v2)
    assert isinstance(viewconf, hg.Viewconf)
    assert viewconf.views and len(viewconf.views) == 2
    assert viewconf.views[0].layout.x == 0
    assert viewconf.views[0].layout.y == 0
    assert viewconf.views[1].layout.x == 0
    assert viewconf.views[1].layout.y == 4


def test_concat_viewconfs():
    v1 = hg.view(hg.track("heatmap"), width=4, height=4).viewconf()
    v2 = hg.view(hg.track("heatmap"), width=5, height=4)

    viewconf = hg.vconcat(v1, v2)
    assert isinstance(viewconf, hg.Viewconf)
    assert viewconf.views and len(viewconf.views) == 2
    assert viewconf.views[0].layout.x == 0
    assert viewconf.views[0].layout.y == 0
    assert viewconf.views[1].layout.x == 0
    assert viewconf.views[1].layout.y == 4

    hg.view(hg.track("heatmap"), width=5, height=3).viewconf()


def test_lock():
    # empty lock throws
    with pytest.raises(AssertionError):
        hg.lock()

    views = [hg.view(hg.track("heatmap")) for _ in range(3)]

    lock = hg.lock(*views, uid="foo")

    assert isinstance(lock, hg.Lock)
    assert lock.uid == "foo"

    for (uid, v), view in zip(lock, views):
        assert uid == view.uid
        assert v == (1, 1, 1)


def test_value_scale_lock():
    # empty lock throws
    with pytest.raises(AssertionError):
        hg.lock()

    tracks = [hg.track("heatmap") for _ in range(3)]
    views = [hg.view(t) for t in tracks]

    lock = hg.lock(*zip(views, tracks), uid="foo")

    assert isinstance(lock, hg.ValueScaleLock)
    assert lock.uid == "foo"

    for (uid, v), (view, track) in zip(lock, zip(views, tracks)):
        assert uid == f"{view.uid}.{track.uid}"
        assert v["track"] == track.uid
        assert v["view"] == view.uid


def test_properties_mixin():
    track = hg.track("heatmap")
    other = track.properties(
        height=500,
    )
    assert track.uid != other.uid
    assert track.height is None
    assert other.height == 500

    other = track.properties(width=400, inplace=True)
    assert track is other
    assert other.uid == track.uid
    assert track.width == 400


def test_options_mixin():
    track = hg.track("heatmap")
    other = track.opts(
        foo="bar",
    )
    assert track.uid != other.uid
    assert track.options is None
    assert other.options and other.options["foo"] == "bar"

    other = track.opts(foo="bar", inplace=True)
    assert track is other
    assert track.uid == other.uid
    assert track.options and track.options["foo"] == "bar"


def test_local_data_mixin():
    track = hg.track("heatmap")
    tsinfo = {"min_pos": [0, 0], "max_pos": [100, 100]}
    data = [{"x": 1, "y": 2}]

    other = track.local_data(tsinfo, data)
    assert track.uid != other.uid
    assert track.data is None
    assert other.data.type == "local-tiles"
    assert other.data.tilesetInfo["x"] == tsinfo
    assert other.data.tiles["x.0.0.0"] == data

    track2 = hg.track("heatmap")
    tsinfo_1d = {"min_pos": [0], "max_pos": [100]}
    other2 = track2.local_data(tsinfo_1d, data, inplace=True)
    assert track2 is other2
    assert track2.data.tiles["x.0.0"] == data

    with pytest.raises(ValueError, match="min_pos and max_pos must have equal lengths"):
        hg.track("heatmap").local_data({"min_pos": [0], "max_pos": [0, 0]}, data)

    with pytest.raises(ValueError, match="min_pos must be a one or two element array"):
        hg.track("heatmap").local_data(
            {"min_pos": [0, 0, 0], "max_pos": [0, 0, 0]}, data
        )


def test_plugin_track():
    """Test that plugin track attributes are maintained after a copy."""
    some_url = "https://some_url"

    # Here we'll create a custom plugin track.
    class PileupTrack(hg.PluginTrack):
        type: Literal["pileup"] = "pileup"
        plugin_url: ClassVar[str] = some_url

    # Specify the track-specific data
    pileup_data = {
        "type": "bam",
        "url": "https://some_url/sorted.bam",
        "chromSizesUrl": "https://some_url/sorted.chromsizes.bam",
        "options": {"maxTileWidth": 30000},
    }

    # Create and use the custom track
    pileup_track = PileupTrack(data=pileup_data)  # ty:ignore[unknown-argument]

    view = hg.view((pileup_track, "top"))
    uid1 = view.uid
    assert view.tracks.top
    assert view.tracks.top[0].plugin_url == some_url

    # The .domain() function creates a copy of the view. We want to make sure
    # that the plugin_url attribute of the PluginTrack is maintained
    view = view.domain(x=(0, 10))
    uid2 = view.uid
    assert view.tracks.top[0].plugin_url == some_url

    # Check to make sure the copy behavior changed the uid as expected
    assert uid1 != uid2
