# HiGlass Docs

Documentation for all HiGlass software ([viewer][hgv], [app][hga], [server][hgs], [docker][hgd])

Simple edits can be made in GitHub. For anything more extensive, build and preview it locally:

```
uv run build.py
uv run python -m http.server 8000 --directory _build/html
```

Then open your browser to `http://localhost:8000`.

Docs are built and deployed via GitHub Actions via a [workflow](.github/workflows/docs.yml).

[hga]: https://github.com/higlass/higlass-app
[hgd]: https://github.com/higlass/higlass-docker
[hgs]: https://github.com/higlass/higlass-server
[hgv]: https://github.com/higlass/higlass
