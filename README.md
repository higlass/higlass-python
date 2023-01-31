# higlass-python v2 🔎

a fresh python library for [`higlass`](https://github.com/higlass/higlass) built 
on top of [`higlass-schema`](https://github.com/higlass/higlass-schema) and
[`higlass-widget`](https://github.com/higlass/higlass-widget).

[![License](https://img.shields.io/pypi/l/higlass-python.svg?color=green)](https://github.com/higlass/higlass-python/raw/master/LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/higlass/higlass-python/blob/main/notebooks/Examples.ipynb)

## Usage

```python
import higlass as hg

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

## Development

Create a virtual environment with Jupyter installed.

```bash
conda create -n higlass python=3.11 jupyterlab
```

Install the package in _editable_ mode. The `.[dev]` ensures that you also install linting/testing tools.

```bash
pip install -e ".[dev]"
```

Our CI checks formatting, linting, and tests. You can run each of these locally with `

You can format the code with `black src/` and lint with `ruff src/`. Tests are executed with `pytest`

# editing the docs




