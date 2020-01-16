from higlass.utils import fill_filetype_and_datatype


def test_fill_filetype_and_datatype():
    filetype, datatype = fill_filetype_and_datatype("myfile.mcool")

    assert filetype == "cooler"
    assert datatype == "matrix"

    filetype, datatype = fill_filetype_and_datatype("myfile.xyz")

    assert not filetype
    assert not datatype
