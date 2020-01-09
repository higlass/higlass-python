import matplotlib.pyplot as plt


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
