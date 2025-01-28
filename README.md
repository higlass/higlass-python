# higlass-python 🔎

A fresh Python library for [`higlass`](https://github.com/higlass/higlass) built
on top of:
* [`higlass-schema`](https://github.com/higlass/higlass-schema): Pydantic models for HiGlass.
* [`higlass-widget`](https://github.com/higlass/higlass-widget): A cross-platform [AnyWidget](https://github.com/manzt/anywidget) for Jupyter environments.

[![License](https://img.shields.io/pypi/l/higlass-python.svg?color=green)](https://github.com/higlass/higlass-python/raw/main/LICENSE)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/higlass/higlass-python/blob/main/examples/Examples.ipynb)

## Installation

```sh
pip install higlass-python
```

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

To learn more about the new API, check out the
[updated documentation](http://docs-python.higlass.io/).

## Upgrade Guide

**higlass-python** v1.0 is a total rewrite of our prior
implementation, aimed to offer a more ergonomic and flexible API. While this
might present challenges when upgrading existing code, we've prepared
[documentation](http://docs-python.higlass.io/) to guide you through the new API usage.

If you find a missing feature, please open an issue – we're committed to
supporting your use cases with the new API.

Despite the large changes in v1.0, we will strive to avoid breaking changes
going forward. However, because of the complete rewrite, the v1.0 release
doesn't strictly adhere to semantic versioning. You can think of it as a pre-1.0
release, with breaking changes and new features included in minor releases, and
bug fixes in patch releases.

We will aim for strict semantic versioning with the v2.0 release. Your feedback
and understanding are greatly appreciated.

## Development

**higlass-python** uses uses [uv](https://astral.sh/uv) for development.

### Commands Cheatsheet

All commands are run from the root of the project, from a terminal:

| Command | Action |
|---------|--------|
| `uv run ruff check --fix && uv run ruff format` | Lint and apply formatting |
| `uv run check` | Check linting rules |
| `uv run ruff format --check` | Check formatting |
| `uv run pytest` | Run unit tests |
| `uv run docs/build.py` | Build the documentation in `docs/_build/html` |

This table now includes only the UV-related commands, with each command in the
left column and its corresponding action in the right column. The formatting is
clean and easy to read.

Our CI enforces formatting, linting, and tests.

## Changelog

Check the [GitHub Releases](https://github.com/higlass/higlass-python/releases) for a detailed changelog.

## Release

Releases are managed via the GitHub UI:

1. [Draft a new release](https://github.com/higlass/higlass-python/releases/new)
2. **Create a tag** in the format `v[major].[minor].[patch]`.
   - *Note:* You can either create the tag in the GitHub UI or select an existing tag created via the Git CLI. The tag triggers publishing to PyPI.
3. **Generate release notes** to summarize changes from merged PRs, and edit.
   - Documentation and CI changes don't belong in release notes
4. Add details for significant changes or migration steps, and ensure titles are clear and consistent.
