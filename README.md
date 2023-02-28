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

**higlass-python** uses [the recommended](https://packaging.python.org/en/latest/flow/#) `hatchling` build-system,
which is convenient to use via the [`hatch` CLI](https://hatch.pypa.io/latest/). We recommend installing `hatch` 
globally (e.g., via `pipx`) and running the various commands defined within `pyproject.toml`. `hatch` will take care
of creating and synchronizing a virtual environment with all dependencies defined in `pyproject.toml`.

### Commands Cheatsheet

All commands are run from the root of the project, from a terminal:

| Command                | Action                                                              |
| :--------------------- | :------------------------------------------------------------------ |
| `hatch run fix`        | Format project with `black .` and apply linting with `ruff --fix .` |
| `hatch run lint`       | Lint project with `ruff .`.                                         |
| `hatch run test`       | Run unit tests with `pytest` in latest Python version.              |
| `hatch run test:test`  | Run unit tests with `pytest` in all target Python versions.         |
| `hatch run docs:build` | Build the documentation in `docs/_build/html`.                      |
| `hatch run docs:serve` | Start an dev-server for live editing RST files in `docs/`.          |

> **Note**: `hatch build` and `hatch publish` are available to build and publish the project to
PyPI, but all releases are handled automatically via CI.

Alternatively, you can develop **higlass-python** by manually creating a virtual environment and
managing installation and dependencies with `pip`. For example, create a virtual environment 
with `conda`:

```bash
conda create -n higlass python=3.11
conda activate higlass
```

and install **higlass-python** in _editable_ mode with all optional dependencies:

```bash
pip install -e ".[dev,fuse,docs]"
```

Our CI checks formatting (`black .`), linting (`ruff .`), and tests (`pytest`).
