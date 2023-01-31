import higlass as hg


def test_basic_track():
    track = hg.track("horizontal-line")
    isinstance(track, hg.EnumTrack)
    assert track.type == "horizontal-line"
