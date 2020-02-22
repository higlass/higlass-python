import os.path as op
import higlass.tilesets as hgti
import pandas as pd
import tempfile


testdir = op.dirname(op.realpath(__file__))


def test_dfpoints():
    df = pd.DataFrame(
        {"a": [1.0, 2.0, 3.0], "b": [5.0, 6.0, 7.0], "x": ["hi", "there", "you"]}
    )

    ts = hgti.dfpoints(df, "a", "b", "x")

    tsinfo = ts.tileset_info()

    assert len(tsinfo["min_pos"]) == 2
    assert "max_width" in tsinfo


def test_beddb():
    """Test the creation of a beddb tileset."""
    ts = hgti.beddb(op.join(testdir, "data/gene_annotations.short.db"))

    tsinfo = ts.tileset_info()

    assert "max_width" in tsinfo

    tiles = ts.tiles(["x.0.0"])

    assert len(tiles) == 1


def test_bigbed():
    ts = hgti.bigbed(op.join(testdir, "data/Ctcf_WT_allMot.bed.short.bb"))

    tsinfo = ts.tileset_info()

    assert "max_width" in tsinfo

    tiles = ts.tiles(["x.0.0"])

    assert len(tiles) == 1


def test_bed2ddb():
    tads = """chr1    1760000 2640000
chr1    2640000 2760000
chr1    2760000 5960000
chr1    5960000 6440000
chr1    6440000 7960000
chr1    7960000 8360000
chr1    8360000 8880000
chr1    8880000 9600000
chr1    9600000 10160000
chr1    10160000        10440000"""

    with tempfile.TemporaryDirectory() as td:
        with open(op.join(td, "tads.bed"), "w") as f:
            f.write(tads)

        import subprocess as sp

        ret = sp.call(
            [
                "clodius",
                "aggregate",
                "bedpe",
                "--chr1-col",
                "1",
                "--chr2-col",
                "1",
                "--from1-col",
                "2",
                "--from2-col",
                "2",
                "--to1-col",
                "3",
                "--to2-col",
                "3",
                "/tmp/tads.bed",
            ]
        )

        ts = hgti.bed2ddb(op.join(td, "tads.bed.multires.db"))
