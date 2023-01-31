# hg 🔎

a fresh python library for [`higlass`](https://github.com/higlass/higlass) built 
on top of [`higlass-schema`](https://github.com/higlass/higlass-schema) and
[`higlass-widget`](https://github.com/higlass/higlass-widget).

[![License](https://img.shields.io/pypi/l/gosling.svg?color=green)](https://github.com/manzt/hg/raw/main/LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/manzt/hg/blob/main/notebooks/Examples.ipynb)


## development

```bash
pip install -e .
jupyter notebook notebooks/Examples.ipynb
```

## usage

```python
import hg

# Remote data source (tileset)
tileset1 = hg.remote(
    uid="CQMd6V_cRw6iCI_-Unl3PQ",
    server="https://higlass.io/api/v1/",
    name="Rao et al. (2014) GM12878 MboI (allreps) 1kb",
)

# Local tileset
tileset2 = hg.cooler("../data/dataset.mcool")

# Create a `hg.HeatmapTrack` for each tileset
track1 = tileset1.track("heatmap")
track2 = tileset2.track("heatmap")

# Create two independent `hg.View`s, one for each heatmap
view1 = hg.view(track1, width=6)
view2 = hg.view(track2, width=6)

# Lock zoom & location for each `View`
view_lock = hg.lock(view1, view2)

# Concatenate views horizontally and apply synchronization lock
(view1 | view2).locks(view_lock)
```

![Side-by-side Hi-C heatmaps, linked by pan and zoom](https://user-images.githubusercontent.com/24403730/159050305-e6a48f03-fba1-4ff7-8eee-2e9c5c40ef88.gif)

