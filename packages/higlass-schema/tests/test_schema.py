import pathlib

import pydantic
import pytest

import higlass_schema as hgs

fixtures = pathlib.Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("path", fixtures.glob("**/*[!invalid,tracks]/*.json"))
def test_valid_viewconf(path: pathlib.Path):
    with path.open() as f:
        hgs.Viewconf[hgs.View[hgs.Track]].model_validate_json(f.read())


@pytest.mark.skip("invalid viewconfs are not yet validated?")
@pytest.mark.parametrize("path", fixtures.glob("test/view-configs-invalid/*.json"))
def test_invalid_viewconf(path: pathlib.Path):
    with pytest.raises(pydantic.ValidationError):
        with path.open() as f:
            hgs.Viewconf[hgs.View[hgs.Track]].model_validate_json(f.read())


@pytest.mark.parametrize("path", fixtures.glob("test/view-configs-tracks/*.json"))
def test_valid_track(path: pathlib.Path):
    # needed to allow testing a union
    class RootTrack(pydantic.RootModel[pydantic.BaseModel]):
        pass

    with path.open() as f:
        RootTrack.model_validate_json(f.read())
