from higlass.client import View, Track, ViewportProjection
from higlass.tilesets import Tileset
import higlass


def test_add_autocomplete():
    """Make sure we add autocomplete if there's gene annotations
    and chromsizes tracks."""
    track1 = Track(
        "horizontal-chromosome-labels",
        server="https://higlass.io/api/v1",
        tilesetUid="xx",
    )

    # chromosome labels should create a genomePositionSearchBox
    view_dict = View([track1], chrominfo=track1).to_dict()
    assert "genomePositionSearchBox" in view_dict

    track2 = Track(
        "horizontal-gene-annotations",
        server="https://higlass.io/api/v1",
        tilesetUid="xx",
    )

    # gene labels alone shouldn't
    view_dict = View([track2], autocomplete=track2).to_dict()
    assert "genomePositionSearchBox" not in view_dict

    view_dict = View([track1, track2], chrominfo=track1, autocomplete=track2).to_dict()
    assert "genomePositionSearchBox" in view_dict


def test_add_tracks():
    """Test combining tracks using the '+' operator."""
    track1 = Track("top-axis")
    track2 = Track("top-axis")

    track3 = track1 + track2

    assert track1 in track3.tracks

    track4 = Track("top-axis")
    track5 = track3 + track4

    assert len(track5.tracks) == 3


def test_divided_track():
    """Test creating a divided track."""
    ts1 = Tileset(uuid="ts1")
    tr1 = Track(track_type="heatmap", server="server1", tileset=ts1)

    ts2 = Tileset(uuid="ts2")
    tr2 = Track(track_type="heatmap", server="server2", tileset=ts2)

    tr3 = tr1 / tr2

    assert "data" in tr3.conf
    assert tr3.conf["data"]["type"] == "divided"


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
