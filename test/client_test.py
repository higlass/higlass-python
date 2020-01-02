from higlass.client import Track, View, ViewportProjection
import higlass


def test_add_tracks():
    """Test combining tracks using the '+' operator."""
    track1 = Track("top-axis")
    track2 = Track("top-axis")

    track3 = track1 + track2

    assert track1 in track3.tracks

    track4 = Track("top-axis")
    track5 = track3 + track4

    assert len(track5.tracks) == 3


def test_combined_track_from_track_list():
    """Test creating a CombinedTrack by providing a list
    of tracks when creating a View."""
    track1 = Track("top-axis")
    track2 = Track("horizontal-line")

    view = View([[track1, track2]])

    view_dict = view.to_dict()
    combined_track = view_dict["tracks"]["top"][0]

    assert combined_track["type"] == "combined"
    assert combined_track["contents"][0]["type"] == "top-axis"


def test_viewport_projection():
    """Test creating a ViewportProjection track."""
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
