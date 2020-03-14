import matplotlib.pyplot as plt
import os.path as op
import sys


def hg_cmap(cmap_name, resolution=256, reverse=False):
    """
    Create a higlass-compatible colormap from a matplotlib
    colormap.

    Parameters
    ----------
    cmap_name (string):
        The name of the color map.
    """
    cmap = plt.get_cmap(cmap_name)

    hg_cmap = []

    for i in range(resolution):
        v = [int(256 * j) for j in cmap(i)]
        hg_cmap += [f"rgba({v[0]}, {v[1]}, {v[2]}, 1.0)"]

    if reverse:
        return hg_cmap[::-1]

    return hg_cmap


def recommend_filetype(filename):
    ext = op.splitext(filename)
    if op.splitext(filename)[1] == ".bed":
        return "bedfile"
    if op.splitext(filename)[1] == ".bedpe":
        return "bedpe"


def recommend_datatype(filetype):
    if filetype == "bedfile":
        return "bedlike"


FILETYPES = {
    "cooler": {
        "description": "multi-resolution cooler file",
        "extensions": [".mcool"],
        "datatypes": ["matrix"],
    },
    "bigwig": {
        "description": "Genomics focused multi-resolution vector file",
        "extensions": [".bw", ".bigwig"],
        "datatypes": ["vector"],
    },
    "beddb": {
        "description": "SQLite-based multi-resolution annotation file",
        "extensions": [".beddb", ".multires.db"],
        "datatypes": ["bedlike", "gene-annotations"],
    },
    "hitile": {
        "description": "Multi-resolution vector file",
        "extensions": [".hitile"],
        "datatypes": ["vector"],
    },
    "time-interval-json": {
        "description": "Time interval notation",
        "extensions": [".htime"],
        "datatypes": ["time-interval"],
    },
    "bam": {
        "description": "Binary alignment map",
        "extensions": [".bam"],
        "datatypes": ["alignments"],
    }
}


def infer_filetype(filename):
    _, ext = op.splitext(filename)

    for filetype, meta in FILETYPES.items():
        if ext.lower() in meta["extensions"]:
            return filetype

    return None


def infer_datatype(filetype):
    if filetype in FILETYPES:
        return FILETYPES[filetype]["datatypes"][0]

    return None


def fill_filetype_and_datatype(filename, filetype=None, datatype=None):
    """
    If no filetype or datatype are provided, add them
    based on the given filename.
    Parameters:
    ----------
    filename: str
        The name of the file
    filetype: str
        The type of the file (can be None)
    datatype: str
        The datatype for the data in the file (can be None)
    Returns:
    --------
    (filetype, datatype): (str, str)
        Filled in filetype and datatype based on the given filename
    """
    if filetype is None:
        # no filetype provided, try a few common filetypes
        filetype = infer_filetype(filename)

        if filetype is None:
            recommended_filetype = recommend_filetype(filename)

            print(
                "Unknown filetype, please specify using the --filetype option",
                file=sys.stderr,
            )
            if recommended_filetype is not None:
                print(
                    "Based on the filename, you may want to try the filetype: {}".format(
                        recommended_filetype
                    )
                )

            return (None, None)

    if datatype is None:
        datatype = infer_datatype(filetype)

        if datatype is None:
            recommended_datatype = recommend_datatype(filetype)
            print(
                "Unknown datatype, please specify using the --datatype option",
                file=sys.stderr,
            )
            if recommended_datatype is not None:
                print(
                    "Based on the filetype, you may want to try the datatype: {}".format(
                        recommended_datatype
                    )
                )

    return filetype, datatype
