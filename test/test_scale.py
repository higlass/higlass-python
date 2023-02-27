import pytest
from higlass._scale import Scale


@pytest.fixture
def scale():
    chromsizes = [("chr1", 10000), ("chr2", 20000), ("chr3", 30000)]
    binsize = 1000
    return Scale(chromsizes, binsize)


def get_data():
    # (gpos, offset, binstart)
    return [
        (("chr1", 0), 0, ("chr1", 0)),
        (("chr1", 900), 0, ("chr1", 0)),
        (("chr1", 1000), 1, ("chr1", 1000)),
        (("chr1", 9000), 9, ("chr1", 9000)),
        (("chr1", 9999), 9, ("chr1", 9000)),
        (("chr1", 10000), 9, ("chr1", 9000)),
        (("chr1", 100000), 9, ("chr1", 9000)),
        (("chr2", 0), 10, ("chr2", 0)),
        (("chr2", 900), 10, ("chr2", 0)),
        (("chr2", 1000), 11, ("chr2", 1000)),
        (("chr2", 19000), 29, ("chr2", 19000)),
        (("chr2", 19999), 29, ("chr2", 19000)),
        (("chr2", 20000), 29, ("chr2", 19000)),
        (("chr2", 100000), 29, ("chr2", 19000)),
        (("chr3", 0), 30, ("chr3", 0)),
        (("chr3", 900), 30, ("chr3", 0)),
        (("chr3", 1000), 31, ("chr3", 1000)),
        (("chr3", 29000), 59, ("chr3", 29000)),
        (("chr3", 29999), 59, ("chr3", 29000)),
        (("chr3", 30000), 59, ("chr3", 29000)),
        (("chr3", 100000), 59, ("chr3", 29000)),
    ]


@pytest.mark.parametrize("gpos, offset, binstart", get_data())
def test_call(scale, gpos, offset, binstart):
    assert scale(gpos) == offset


@pytest.mark.parametrize("gpos, offset, binstart", get_data())
def test_invert(scale, gpos, offset, binstart):
    assert scale.invert(offset) == binstart


def test_call_out_of_bounds(scale):
    assert scale(("chr1", -1)) == 0
    assert scale(("chr3", 30000)) == 59


def test_invert_out_of_bounds(scale):
    assert scale.invert(-1) == ("chr1", 0)
    assert scale.invert(60) == ("chr3", 29000)


def test_rebin(scale):
    new_scale = scale.rebin(500)
    assert scale.binsize == 1000
    assert scale.n_bins == 60
    assert new_scale.binsize == 500
    assert new_scale.n_bins == 120
