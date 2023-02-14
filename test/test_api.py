import higlass as hg


def test_basic_track():
    track = hg.track("horizontal-line")
    isinstance(track, hg.EnumTrack)
    assert track.type == "horizontal-line"


def test_viewport_projection():
    v1 = hg.view(hg.track("heatmap"))
    v2 = hg.view(hg.track("heatmap"))

    v3 = v1.project(v2, on="top")
    assert v3.tracks.top and v3.tracks.top[0].type == "viewport-projection-horizontal"

    v4 = v2.project(v1, on="center", inplace=True)
    assert v2 == v4
    assert v2.tracks.center and v2.tracks.center[1].type == "viewport-projection-center"
