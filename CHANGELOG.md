## [v1.2.1](https://github.com/higlass/higlass-python/compare/v1.2.0...v1.2.1)

- Calculate file pointer hash for track uids for tileset tracks
- Fix view copy behavior to preserve specific plugin track class vars

## [v1.2.0](https://github.com/higlass/higlass-python/compare/v1.1.2...v1.2.0)

- **Breaking**: Migrate to higlass-schema v0.2.0 (pydantic v2)
- Shorter automatic uids for Tracks and Views
- Upgrade HiGlass front-end to v1.13

This release does not introduce changes to the `higlass-python` API itself. However, it migrates the core data objects created and modified by the `higlass-python` API from Pydantic v1 to Pydantic v2. We are marking this as a **breaking release**, as some methods and attributes on these objects are now deprecated. 

Libraries relying on `higlass-schema` (Pydantic models for Python) may encounter breaking changes if they use methods that have changed between Pydantic v1 and v2. We expect this update to improve compatibility and make it easier to use `higlass-python` in environments that depend on Pydantic v2 (which are increasing).

## [v1.1.2](https://github.com/higlass/higlass-python/compare/v1.1.1...v1.1.2)

- Pin higlass-schema version upper bound for <v1.2

## [v1.1.1](https://github.com/higlass/higlass-python/compare/v1.1.0...v1.1.1)

- Upgrade anywidget version
- Add vertical track variants for auto layout

## [v1.1.0](https://github.com/higlass/higlass-python/compare/v1.0.3...v1.1.0)

- Add bedlike file support

## [v1.0.3](https://github.com/higlass/higlass-python/compare/v1.0.2...v1.0.3)

- Ensure JS is included in PyPI wheel

## [v1.0.2](https://github.com/higlass/higlass-python/compare/v1.0.1...v1.0.2)

- Added docs on passing in an auth header
- Ensure JS is included in PyPI wheel

## [v1.0.1](https://github.com/higlass/higlass-python/compare/v1.0.1...v1.0.0)

- Pass kwargs in to Viewconf.widget() so that they can be passed on to the higlass widget and potentially make their way to the higlass component

## [v0.4.8](https://github.com/higlass/higlass-python/compare/v0.4.8...v0.4.7)

- Bumped higlass version

## [v0.4.7](https://github.com/higlass/higlass-python/compare/v0.4.7...v0.4.6)

- Bumped pillow version

## [v0.4.6](https://github.com/higlass/higlass-python/compare/v0.4.6...v0.4.5)

- Added inline_tile support for bed-like items
- Bumped React version dependency to ensure compatibility with latest  Juptyerlab
- Bumped higlass version to v1.11.8
- Bumped matplotlib version and added pillow dependency version

## [v0.4.5](https://github.com/higlass/higlass-python/compare/v0.4.5...v0.4.4)

- Add constructor for multivec tilesets
- Added wrapper for bam tileset generator
- Updated docs to include examples for bam and multivec tilesets
- Add proxy support
- Add support for listening on a unix socket

## [v0.4.4](https://github.com/higlass/higlass-python/compare/v0.4.4...v0.4.3)

-   Added default positions for non `horizontal-` tracks
-   Update docs to include Views import in simple example
-   Bump HiGlass to v1.11

## [v0.4.2](https://github.com/higlass/higlass-python/compare/v0.4.2...v0.4.1)

-   Only load FUSE python package when it is called to avoid libfuse missing error

## [v0.4.1](https://github.com/higlass/higlass-python/compare/v0.4.1...v0.4.0)

-   Add missing `pixi.js` dependency from `higlass-jupyter`
-   Update `@jupyter-widgets/base` to support Jupyter Lab v2
-   Update simple-httpfs to fix the missing `boto3` error

## [v0.4.0](https://github.com/higlass/higlass-python/compare/v0.4.0...v0.3.0)

-   API for adding genome position search box within python
-   Removed default log file creation. Servers now log to in-memory stream by default.
-   Copied Python docs over from the higlass repo
-   Added `save_as_png` function
-   Added section on track types and multiple views to the docs
-   Overloaded '+' operator to for combining tracks and creating CombinedTracks
-   Added `ViewProjection` track
-   Remove the higlass-python.log files that are created everywhere
-   Overloaded the '/' operator to create divided tracks
-   Added support using matplotlib colormaps
-   Created simplified view creation API
-   Add auth_token parameter to higlass.display
-   Use higlass v1.8.1
-   Parameters for turning on the genome position search box

## [v0.3.0](https://github.com/higlass/higlass-python/compare/v0.2.1...v0.3.0)

-   Support multiple overlays and allow to set the `uid` and `type` options manually
-   Add support for value locks via the new `value_scale_syncs` argument of `display()` and `ViewConf`
-   Allow not starting FUSE by passing `no_fuse=True` to `display()`
-   Update the HiGlass JavaScript library to `v1.7`

## [v0.2.1](https://github.com/higlass/higlass-python/compare/v0.2.0...v0.2.1)

-   Fixed #30: Example working again
-   Fixed `overlay` property by making it a property of `Views`. Also updated HiGlass to v1.6.11 to properly render overlays.

## [v0.2.0](https://github.com/higlass/higlass-python/compare/v0.1.13...v0.2.0)

-   Implement two-way data bindings via traitlets. See [notebooks/two-way-data-binding.ipynb](notebooks/two-way-data-binding.ipynb) for an example
-   Add `overlays` to `display` and `ViewConf` to be able to define overlays
-   Store HiGlass' JavaScript API on the widget's root container. This container can be found via a random ID that is stored in `widget.dom_element_id`

## [v0.1.14](https://github.com/higlass/higlass-python/compare/v0.1.13...v0.1.14)

-   Add compatibility with JupyterLab `v1` and ipywidgets `v7.5`
-   Bumped HiGlass to `v1.6`

## [v0.1.13](https://github.com/higlass/higlass-python/compare/v0.1.12...v0.1.13)

-   Added top-level exports of `view`, `display`, `Tileset`, `Server`, `Track`, `CombinedTrack`, `View`, and `ViewConf`

## [v0.1.12](https://github.com/higlass/higlass-python/compare/v0.1.11...v0.1.12)

-   Expose dark mode in `higlass.display(dark_mode=True)`
-   Do not mutate track objects in `higlass.display()` for reusability
-   Further API cleaning. `ViewConf.views` is a list of views now

## [v0.1.11](https://github.com/higlass/higlass-python/compare/v0.1.10...v0.1.11)

-   Convenience function for loading 2d labeled points from a dataframe.
-   Remove Flask-related debugging and uninformative logs
-   Add `__repr__` to `ViewConf` for convenience

## [v0.1.10](https://github.com/higlass/higlass-python/compare/v0.1.8...v0.1.10)

-   Synchronized Python and node package versions

## [v0.1.8](https://github.com/higlass/higlass-python/compare/v0.1.7...v0.1.8)

-   Fix installation

## [v0.1.7](https://github.com/higlass/higlass-python/compare/v0.1.1...v0.1.7)

-   Bumped higlass version to `v1.5`
-   Added CombinedTrack
-   Added change_atributes and change_options functions

## [v0.1.1](https://github.com/higlass/higlass-python/releases/tag/v0.1.1)

-   First release
