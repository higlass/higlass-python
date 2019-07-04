from functools import partial
import multiprocess as mp
import cytoolz as toolz
import os.path as op
import platform
import logging
import socket
import json
import time
import os

from flask import Flask
from flask import request, jsonify

# from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

from fuse import FUSE
import requests
import slugid
import sh


__all__ = ["Server"]

OS_NAME = platform.system()

# Disable annoying flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log.disabled = True
# The following line is also needed to turn off all debug logs
os.environ['WERKZEUG_RUN_MAIN'] = 'true'


def create_app(tilesets, name, log_file, log_level, file_ids, fuse=None):
    app = Flask(__name__)
    app.logger.disabled = True
    CORS(app)

    remote_tilesets = {}

    @app.route("/api/v1/")
    def hello():
        return "Hello World!"

    @app.route("/api/v1/register_url/", methods=["POST"])
    def register_url():
        from higlass.tilesets import by_filetype
        js = request.json
        if js["filetype"] not in by_filetype:
            return (
                jsonify({"error":
                    "Unknown filetype: {}".format(js["filetype"])}),
                400,
            )
        if fuse is None:
            return jsonify({"error": "httpfs is not available."})

        key = (js["fileUrl"], js["filetype"])
        if key in remote_tilesets:
            ts = remote_tilesets[key]
        else:
            factory = by_filetype[js["filetype"]]
            ts = factory(fuse.get_filepath(js["fileUrl"]))
            remote_tilesets[key] = ts
        return jsonify({"uid": ts.uuid})

    @app.route("/api/v1/chrom-sizes/", methods=["GET"])
    def chrom_sizes():
        """
        Coordinate system resource.

        Query Parameters
        ----------------
        id : string
            Tileset UUID
        type : { tsv | json }
            Response format. Default is tsv.
        cum : boolean
            Return cumulative lengths. Default is false.

        """
        uuid = request.args.get("id", None)
        res_type = request.args.get("type", "tsv")
        incl_cum = request.args.get("cum", False)

        # filter for tileset
        ts = next(
            (ts for ts in _list_tilesets() if ts.uuid == uuid),
            None)
        if ts is None:
            return jsonify({"error": "Not found"}), 404
        if not hasattr(ts, 'chromsizes'):
            return jsonify({"error": "Tileset does not have chrom sizes."})

        # list of tuples (chrom, size)
        data = ts.chromsizes
        if incl_cum:
            data, _data, cum = [], data, 0
            for chrom, size in _data:
                cum += size
                data.append((chrom, size, cum))

        if res_type == "json":
            if incl_cum:
                j = {
                    ts.uuid: {
                        chrom: {'size': size, 'offset': offset}
                            for chrom, size, offset in data
                    }
                }
            else:
                j = {
                    ts.uuid: {
                        chrom: {"size": size}
                            for chrom, size in data
                    }
                }
            return jsonify(j)
        elif res_type == "tsv":
            if incl_cum:
                return "\n".join(
                    "{}\t{}\t{}".format(chrom, size, offset)
                        for chrom, size, offset in data
                )
            else:
                return "\n".join("{}\t{}".format(chrom, size)
                        for chrom, size in data
                )
        else:
            return jsonify({"error": "Unknown response type"}), 500

    @app.route("/api/v1/uids_by_filename/", methods=["GET"])
    def uids_by_filename():
        return jsonify(
            {
                "count": len(tilesets),
                "results": {i: tilesets[i] for i in range(len(tilesets))},
            }
        )

    def _list_tilesets():
        return tilesets + list(remote_tilesets.values())

    @app.route("/api/v1/tilesets/", methods=["GET"])
    def list_tilesets():
        tsets = _list_tilesets()
        return jsonify(
            {
                "count": len(tsets),
                "next": None,
                "previous": None,
                "results": [ts.meta for ts in tsets],
            }
        )

    @app.route("/api/v1/tileset_info/", methods=["GET"])
    def tileset_info():
        uuids = request.args.getlist("d")

        info = {}
        for uuid in uuids:
            ts = next(
                (ts for ts in _list_tilesets() if ts.uuid == uuid),
                None)

            if ts is not None:
                info[uuid] = ts.tileset_info()
            else:
                info[uuid] = {
                    "error": "No such tileset with uid: {}".format(uuid)
                }

        return jsonify(info)

    @app.route("/api/v1/tiles/", methods=["GET"])
    def tiles():
        tids_requested = set(request.args.getlist("d"))

        if not tids_requested:
            return jsonify({"error": "No tiles requested"}), 400

        extract_uuid = lambda tid: tid.split(".")[0]
        uuids_to_tids = toolz.groupby(extract_uuid, tids_requested)

        tiles = []
        for uuid, tids in uuids_to_tids.items():
            ts = next(
                (ts for ts in _list_tilesets() if ts.uuid == uuid),
                None)
            tiles.extend(ts.tiles(tids))
        data = {tid: tval for tid, tval in tiles}
        return jsonify(data)

    logging.basicConfig(
        level=log_level,
        filename=log_file,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    )

    return app


class ServerError(Exception):
    pass


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


class FuseProcess:
    def __init__(self, tmp_dir):
        self.tmp_dir = tmp_dir
        self.http_directory = op.join(tmp_dir, "http")
        self.https_directory = op.join(tmp_dir, "https")
        self.diskcache_directory = op.join(tmp_dir, "dc")

    def setup(self):
        """
        Set up filesystem in user space for http and https
        so that we can retrieve tiles from remote sources.

        Parameters
        ----------
        tmp_dir: string
            The temporary directory where to create the
            http and https directories
        """
        from simple_httpfs import HttpFs

        if not op.exists(self.http_directory):
            os.makedirs(self.http_directory)
        if not op.exists(self.https_directory):
            os.makedirs(self.https_directory)
        if not op.exists(self.diskcache_directory):
            os.makedirs(self.diskcache_directory)

        self.teardown()

        disk_cache_size = 2 ** 25
        lru_capacity = 400

        def start_fuse(directory, protocol):
            try:
                # This is a bit confusing. I think `fuse` (lowercase) is used
                # above in get_filepath() line 50 and 52. If that's not the
                # case than this assignment is useless and get_filepath() is
                # broken
                fuse = FUSE(
                    HttpFs(
                        protocol,
                        disk_cache_size=disk_cache_size,
                        disk_cache_dir=self.diskcache_directory,
                        lru_capacity=lru_capacity,
                    ),
                    directory,
                    foreground=False,
                    #allow_other=True
                )
            except RuntimeError as e:
                if str(e) != "1":
                    raise e

        proc1 = mp.Process(
            target=start_fuse, args=[self.http_directory, 'http']
        )
        proc1.start()
        proc1.join()

        proc2 = mp.Process(
            target=start_fuse, args=[self.https_directory, 'https']
        )
        proc2.start()
        proc2.join()

    def teardown(self):
        try:
            if OS_NAME == 'Darwin':
                sh.umount("HttpFs")
                sh.umount(self.http_directory)
            else:
                sh.fusermount("-uz", self.http_directory)
        except Exception:
            pass

        try:
            if OS_NAME == 'Darwin':
                sh.umount("HttpFs")
                sh.umount(self.https_directory)
            else:
                sh.fusermount("-uz", self.https_directory)
        except Exception:
            pass

    def get_filepath(self, url):
        """
        Get the httpfs mount filepath from a url

        """
        if url[:7] == "http://":
            return self.http_directory + url[6:] + ".."
        elif url[:8] == "https://":
            return self.https_directory + url[7:] + ".."
        else:
            raise ValueError("Unsupported URL protocol")


class Server:
    """
    A lightweight HiGlass server.
    """

    # Keep track of the server processes that have been started.
    # So that when someone says 'start', the old ones are terminated
    processes = {}
    diskcache_directory = "/tmp/hgflask/dc"

    def __init__(
        self, tilesets, port=None, host="localhost", tmp_dir="/tmp/hgflask"
    ):
        """
        Maintain a reference to a running higlass server

        Parameters
        ----------
        port: int
            The port that this server will run on
        tileset: []
            A list of tilesets to serve (see higlass.tilesets)
        host: string
            The host this server is running on.  Usually just localhost
        tmp_dir: string
            A temporary directory into which to mount the http and https files

        """
        self.tilesets = tilesets
        self.host = host
        self.port = port
        self.tmp_dir = tmp_dir
        self.file_ids = dict()
        self.fuse_process = FuseProcess(tmp_dir)
        self.fuse_process.setup()

    def start(self, log_file="/tmp/hgserver.log", log_level=logging.INFO):
        """
        Start a lightweight higlass server.

        Parameters
        ----------
        log_file: string
            Where to place diagnostic log files
        log_level: logging.*
            What level to log at
        """
        for puid in list(self.processes.keys()):
            self.processes[puid].terminate()
            del self.processes[puid]

        self.app = create_app(
            self.tilesets,
            __name__,
            log_file=log_file,
            log_level=log_level,
            file_ids=self.file_ids,
            fuse=self.fuse_process
        )

        # we're going to assign a uuid to each server process so that if
        # anything goes wrong, the variable referencing the process doesn't get
        # lost
        uuid = slugid.nice()
        if self.port is None:
            self.port = get_open_port()
        target = partial(
            self.app.run,
            threaded=True,
            debug=True,
            host="0.0.0.0",
            port=self.port,
            use_reloader=False,
        )
        self.processes[uuid] = mp.Process(target=target)
        self.processes[uuid].start()
        self.connected = False
        while not self.connected:
            try:
                url = "http://{}:{}/api/v1".format(self.host, self.port)
                r = requests.head(url)
                if r.ok:
                    self.connected = True
            except requests.ConnectionError:
                time.sleep(0.2)

    def stop(self):
        """
        Stop this server so that the calling process can exit
        """
        # unsetup_fuse()
        self.fuse_process.teardown()
        for uuid in self.processes:
            self.processes[uuid].terminate()

    def tileset_info(self, uid):
        """
        Return the tileset info for the given tileset
        """
        url = "http://{host}:{port}/api/v1/tileset_info/?d={uid}".format(
            host=self.host, port=self.port, uid=uid
        )

        req = requests.get(url)
        if req.status_code != 200:
            raise ServerError("Error fetching tileset_info:", req.content)

        content = json.loads(req.content)
        return content[uid]

    def tiles(self, uid, z, x, y=None):
        """
        Return tiles from the specified dataset (uid) at
        the given position (z,x,[u])
        """
        tile_id = "{uid}.{z}.{x}".format(uid=uid, z=z, x=x)
        if y is not None:
            tile_id += ".{y}".format(y=y)
        url = "http://{host}:{port}/api/v1/tiles/?d={tile_id}".format(
            host=self.host, port=self.port, tile_id=tile_id
        )

        req = requests.get(url)
        if req.status_code != 200:
            raise ServerError("Error fetching tile:", req.content)

        content = json.loads(req.content)
        return content[tile_id]

    def chromsizes(self, uid):
        """
        Return the chromosome sizes from the given filename
        """
        url = "http://{host}:{port}/api/v1/chrom-sizes/?id={uid}".format(
            host=self.host, port=self.port, uid=uid
        )

        req = requests.get(url)
        if req.status_code != 200:
            raise ServerError("Error fetching chromsizes:", req.content)

        return req.content

    @property
    def api_address(self):
        return "http://{host}:{port}/api/v1".format(host=self.host, port=self.port)
