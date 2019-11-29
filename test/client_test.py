from higlass.client import Track, View, ViewportProjection
import higlass


def test_add_tracks():
    track1 = Track("top-axis")
    track2 = Track("top-axis")

    track3 = track1 + track2

    assert track1 in track3.tracks

    track4 = Track("top-axis")
    track5 = track3 + track4

    assert track1 in track5.tracks
    assert track4 in track5.tracks


def test_viewport_projection():
    track1 = Track("top-axis")
    view1 = View([track1])

    vp = ViewportProjection(view1)

    track2 = Track("top-axis")
    track3 = track2 + vp

    assert vp.conf["type"] == "viewport-projection"
    assert track3.tracks[1].conf["type"] == "viewport-projection-horizontal"

    track4 = Track("heatmap")
    track5 = track4 + vp

    assert track5.tracks[1].conf["type"] == "viewport-projection-center"
