import pathlib

import higlass_schema as hgs
import pydantic
import pytest

fixtures = pathlib.Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("path", fixtures.glob("**/*[!invalid,tracks]/*.json"))
def test_valid_viewconf(path: pathlib.Path):
    hgs.Viewconf[hgs.View[hgs.Track]].parse_file(path)


@pytest.mark.skip("invalid viewconfs are not yet validated?")
@pytest.mark.parametrize("path", fixtures.glob("test/view-configs-invalid/*.json"))
def test_invalid_viewconf(path: pathlib.Path):
    with pytest.raises(pydantic.ValidationError):
        hgs.Viewconf[hgs.View[hgs.Track]].parse_file(path)


@pytest.mark.parametrize("path", fixtures.glob("test/view-configs-tracks/*.json"))
def test_valid_track(path: pathlib.Path):
    # needed to allow testing a union
    class RootTrack(pydantic.BaseModel):
        __root___: hgs.Track

    RootTrack.parse_file(path)
