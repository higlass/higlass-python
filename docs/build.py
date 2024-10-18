# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "higlass-python",
#     "markupsafe==2.0.1",
#     "setuptools",
#     "sphinx-js",
#     "Sphinx",
# ]
#
# [tool.uv.sources]
# higlass-python = { path = "../" }
# ///
import pathlib

from sphinx.application import Sphinx

SELF_DIR = pathlib.Path(__file__).parent


def main():
    app = Sphinx(
        srcdir=SELF_DIR,
        confdir=SELF_DIR,
        outdir=SELF_DIR / "_build" / "html",
        doctreedir=SELF_DIR / "_build" / "doctrees",
        buildername="html",
    )

    app.build()


if __name__ == "__main__":
    main()
