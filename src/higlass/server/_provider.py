import itertools
import os
import weakref
from dataclasses import dataclass
from typing import List, MutableMapping, Optional

import starlette.applications
import starlette.middleware.cors
import starlette.requests
import starlette.responses
import starlette.routing

from higlass.api import track
from higlass.tilesets import LocalTileset
from higlass.utils import TrackType, _datatype_default_track

from ._background_server import BackgroundServer


@dataclass(frozen=True)
class TilesetResource:
    tileset: LocalTileset
    provider: "TilesetProvider"

    @property
    def server(self) -> str:
        return f"{self.provider.url}/api/v1/"

    def track(self, type_: Optional[TrackType] = None, **kwargs):
        # use default track based on datatype if available
        if type_ is None:
            if self.tileset.datatype is None:
                raise ValueError("No default track for tileset")
            else:
                type_ = _datatype_default_track[self.tileset.datatype]  # type: ignore
        t = track(
            type_=type_,  # type: ignore
            server=self.server,
            tilesetUid=self.tileset.uid,
            **kwargs,
        )
        if self.tileset.name:
            t.opts(name=self.tileset.name, inplace=True)
        return t


def get_list(query: str, field: str) -> List[str]:
    """Parse chained query params into list.
    >>> get_list("d=id1&d=id2&d=id3", "d")
    ['id1', 'id2', 'id3']
    >>> get_list("d=1&e=2&d=3", "d")
    ['1', '3'].
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

    def chromsizes(request: starlette.requests.Request):
        """Return chromsizes for given tileset id as TSV."""
        uid = request.query_params.get("id")
        tileset_resource = tileset_resources[uid]
        info = tileset_resource.info()
        assert "chromsizes" in info, "No chromsizes in tileset info"
        return starlette.responses.PlainTextResponse(
            "\n".join(f"{chrom}\t{size}" for chrom, size in info["chromsizes"])
        )

    return starlette.routing.Mount(
        path="/api/v1",
        routes=[
            starlette.routing.Route("/tileset_info/", endpoint=tileset_info),
            starlette.routing.Route("/tiles/", endpoint=tiles),
            starlette.routing.Route("/chrom-sizes/", endpoint=chromsizes),
        ],
    )


class TilesetProvider(BackgroundServer):
    _tilesets: MutableMapping[str, LocalTileset]
    proxy: bool = False

    def __init__(self, allowed_origins: Optional[List[str]] = None):
        if allowed_origins is None:
            allowed_origins = ["*"]
        self._tilesets = weakref.WeakValueDictionary()
        app = starlette.applications.Starlette(
            routes=[
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
        if self.proxy:
            return f"/proxy/{self.port}"

        # https://github.com/yuvipanda/altair_data_server/blob/4d6ffcb19f864218c8d825ff2c95a1c8180585d0/altair_data_server/_altair_server.py#L73-L93
        if "JUPYTERHUB_SERVICE_PREFIX" in os.environ:
            urlprefix = os.environ["JUPYTERHUB_SERVICE_PREFIX"]
            return f"{urlprefix}/proxy/{self.port}"

        return f"http://localhost:{self.port}"

    def create(self, tileset: LocalTileset) -> TilesetResource:
        resource = TilesetResource(tileset, provider=self)
        self._tilesets[tileset.uid] = tileset
        self.start()
        return resource
