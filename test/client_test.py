from higlass.client import View, Track


def test_add_autocomplete():
    """Make sure we add autocomplete if there's gene annotations
    and chromsizes tracks."""
    track1 = Track(
        "horizontal-chromosome-labels",
        server="https://higlass.io/api/v1",
        tilesetUid="xx",
    )

    # chromosome labels should create a genomePositionSearchBox
    view_dict = View([track1]).to_dict()
    assert "genomePositionSearchBox" in view_dict

    track2 = Track(
        "horizontal-gene-annotations",
        server="https://higlass.io/api/v1",
        tilesetUid="xx",
    )

    # gene labels alone shouldn't
    view_dict = View([track2]).to_dict()
    assert "genomePositionSearchBox" not in view_dict

    view_dict = View([track1, track2]).to_dict()
    assert "genomePositionSearchBox" in view_dict
