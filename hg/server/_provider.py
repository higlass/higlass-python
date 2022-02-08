import itertools
import weakref
from dataclasses import dataclass
from typing import List, MutableMapping, Optional

import starlette.applications
import starlette.middleware.cors
import starlette.requests
import starlette.responses
import starlette.routing

from hg.api import track
from hg.utils import TrackType
from hg.tilesets import LocalTileset

from ._background_server import BackgroundServer

_datatype_default_track = {
    "2d-rectangle-domains": "2d-rectangle-domains",
    "bedlike": "bedlike",
    "chromsizes": "horizontal-chromosome-labels",
    "gene-annotations": "horizontal-gene-annotations",
    "matrix": "heatmap",
    "vector": "horizontal-bar",
    "multivec": "horizontal-multivec",
}


@dataclass(frozen=True)
class TilesetResource:
    tileset: LocalTileset
    provider: "TilesetProvider"

    @property
    def server(self) -> str:
        return f"{self.provider.url}/api/v1/"

    def track(self, type: Optional[TrackType] = None, **kwargs):
        # use default track based on datatype if available
        if type is None:
            if self.tileset.datatype is None:
                raise ValueError("No default track for tileset")
            else:
                type = _datatype_default_track[self.tileset.datatype]  # type: ignore
        return track(
            type_=type,  # type: ignore
            server=self.server,
            tilesetUid=self.tileset.uid,
            **kwargs,
        )


def get_list(query: str, field: str) -> List[str]:
    """Parse chained query params into list.
    >>> get_list("d=id1&d=id2&d=id3", "d")
    ['id1', 'id2', 'id3']
    >>> get_list("d=1&e=2&d=3", "d")
    ['1', '3']
    """
    kv_tuples = [x.split("=") for x in query.split("&")]
    return [v for k, v in kv_tuples if k == field]


# adapted from https://github.com/higlass/higlass-python/blob/b3be6e49cbcab6be72eb0ad65c68a286161b8682/higlass/server.py#L169-L199
def create_tileset_route(tileset_resources: MutableMapping[str, LocalTileset]):
    def tileset_info(request: starlette.requests.Request):
        uids = get_list(request.url.query, "d")
        info = {
            uid: tileset_resources[uid].info()
            if uid in tileset_resources
            else {"error": f"No such tileset with uid: {uid}"}
            for uid in uids
        }
        return starlette.responses.JSONResponse(info)

    def tiles(request: starlette.requests.Request):
        requested_tids = set(get_list(request.url.query, "d"))
        if not requested_tids:
            return starlette.responses.JSONResponse(
                {"error": "No tiles requested"}, 400
            )

        tiles: list = []
        for uid, tids in itertools.groupby(
            iterable=sorted(requested_tids), key=lambda tid: tid.split(".")[0]
        ):
            tileset_resource = tileset_resources.get(uid)
            if not tileset_resource:
                return starlette.responses.JSONResponse(
                    {"error": f"No tileset found for requested uid: {uid}"}, 400
                )
            tiles.extend(tileset_resource.tiles(list(tids)))
        data = {tid: tval for tid, tval in tiles}
        return starlette.responses.JSONResponse(data)

    return starlette.routing.Mount(
        "/api/v1",
        routes=[
            starlette.routing.Route("/tileset_info/", endpoint=tileset_info),
            starlette.routing.Route("/tiles/", endpoint=tiles),
        ],
    )


# dummy route for debugging
def hello(_):
    return starlette.responses.PlainTextResponse("hello, world.")


class TilesetProvider(BackgroundServer):
    _tilesets: MutableMapping[str, LocalTileset]

    def __init__(self, allowed_origins: Optional[List[str]] = None):
        self._tilesets = weakref.WeakValueDictionary()
        app = starlette.applications.Starlette(
            routes=[
                starlette.routing.Route("/", hello),
                create_tileset_route(self._tilesets),
            ]
        )

        # configure cors
        if allowed_origins:
            app.add_middleware(
                starlette.middleware.cors.CORSMiddleware,
                allow_origins=allowed_origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        super().__init__(app)

    @property
    def url(self) -> str:
        return f"http://localhost:{self.port}"

    def create(self, tileset: LocalTileset) -> TilesetResource:
        resource = TilesetResource(tileset, provider=self)
        self._tilesets[tileset.uid] = tileset
        self.start()
        return resource
