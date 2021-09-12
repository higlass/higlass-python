from higlass.trackdata import bedtiles
from tempfile import TemporaryDirectory
from os.path import join


def test_bedtiles():
    with TemporaryDirectory() as tmpdir:
        chromfile = join(tmpdir, "chrom.sizes")
        with open(chromfile, "w") as f:
            f.write("chr1\t1000\n")
            f.write("chr2\t2000\n")
            f.flush()

        lines = [
            ("chr1", 10, 100, "a1", ".", "+"),
            ("chr2", 10, 100, "a2", ".", "+"),
        ]

        data = bedtiles(lines, chromfile)

        tsinfo = data["tilesetInfo"]

        assert tsinfo["x"]["max_width"] == 3000
        assert tsinfo["x"]["max_pos"][0] == 3000

        tiles = data["tiles"]

        assert "x.0.0" in tiles
        assert len(tiles["x.0.0"]) == 2
        assert tiles["x.0.0"][0]["xStart"] == 10

        # second item's start should be offset by chr1's position
        assert tiles["x.0.0"][1]["xStart"] == 1010
        assert tiles["x.0.0"][1]["chrOffset"] == 1000
