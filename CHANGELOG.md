** Next release **

## [v0.2.0](https://github.com/higlass/higlass-python/compare/v0.1.13...v0.2.0)

- Python > JS via traitlets
  - currently only `select_mode` is implemented
- JS > Python via event handlers inspired by QGrid. Add an event listener using `widget.on(eventName, handler)` and remove it with `widget.off(eventName)`
  - `location`, `cursor_location`, and `selection` are supported which correlate to `location`, `cursorLocation`, and `rangeSelection` in the JS world.

## [v0.1.13](https://github.com/higlass/higlass-python/compare/v0.1.12...v0.1.13)

- Add compatibility with JupyterLab `v1` and ipywidgets `v7.5`
- Bumped HiGlass to `v1.6`

## [v0.1.12](https://github.com/higlass/higlass-python/compare/v0.1.11...v0.1.12)

- Expose dark mode in `higlass.display(dark_mode=True)`
- Do not mutate track objects in `higlass.display()` for reusability
- Further API cleaning. `ViewConf.views` is a list of views now

## [v0.1.11](https://github.com/higlass/higlass-python/compare/v0.1.10...v0.1.11)

- Convenience function for loading 2d labeled points from a dataframe.
- Remove Flask-related debugging and uninformative logs
- Add `__repr__` to `ViewConf` for convenience

## [v0.1.10](https://github.com/higlass/higlass-python/compare/v0.1.8...v0.1.10)

- Synchronized Python and node package versions

## [v0.1.8](https://github.com/higlass/higlass-python/compare/v0.1.7...v0.1.8)

- Fix installation

## [v0.1.7](https://github.com/higlass/higlass-python/compare/v0.1.1...v0.1.7)

- Bumped higlass version to `v1.5`
- Added CombinedTrack
- Added change_atributes and change_options functions

## [v0.1.1](https://github.com/higlass/higlass-python/releases/tag/v0.1.1)

- First release
