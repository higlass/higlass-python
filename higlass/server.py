from functools import partial
import multiprocess as mp
import cytoolz as toolz
import os.path as op
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

import higlass.tilesets as hgti


__all__ = ["Server"]


def get_filepath(filepath):
    """
    Get the filepath from a tileset definition
    Parameters
    ----------
    tileset_def: { 'filepath': ..., 'uid': ..., 'filetype': ...}
        The tileset definition
    returns: string
        The filepath, either as specified in the tileset_def or
        None
    """

    if filepath[:7] == "http://":
        filepath = fuse.http_directory + filepath[6:] + ".."
    if filepath[:8] == "https://":
        filepath = fuse.https_directory + filepath[7:] + ".."

    print("******** filepath:", filepath)

    return filepath


def create_app(tilesets, name, log_file, log_level, file_ids):
    app = Flask(__name__)
    CORS(app)

    TILESETS = tilesets

    remote_tilesets = {}

    @app.route("/api/v1/")
    def hello():
        return "Hello World!"

    @app.route("/api/v1/register_url/", methods=["POST"])
    def register_url():
        js = request.json
        key = (js["fileUrl"], js["filetype"])

        if js["filetype"] not in hgti.by_filetype:
            return (
                jsonify({"error": "Unknown filetype: {}".format(js["filetype"])}),
                400,
            )

        if key in remote_tilesets:
            return jsonify({"uid": remote_tilesets[key].uuid})

        new_tileset = hgti.by_filetype[js["filetype"]](get_filepath(js["fileUrl"]))
        remote_tilesets[key] = new_tileset

        return jsonify({"uid": new_tileset.uuid})

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

        ts = next((ts for ts in list_tilesets() if ts.uuid == uuid), None)

        if ts is None:
            return jsonify({"error": "Not found"}), 404

        data = ts.chromsizes()

        new_data = []

        if incl_cum:
            cum = 0
            for (chrom, size) in data:
                new_data += [(chrom, size, cum)]
                cum += size

            for chrom in data.keys():  # dictionaries in py3.6+ are ordered!
                data[chrom]["offset"] = cum
                cum += data[chrom]["size"]

        if res_type == "json":
            # should return
            # { uuid: {
            #   'chr1': {'size': 2343, 'offset': 0},
            #
            if incl_cum:
                j = {
                    ts.uuid: dict(
                        [
                            (chrom, {"size": size, "offset": offset})
                            for (chrom, size, offset) in data
                        ]
                    )
                }
            else:
                j = {ts.uuid: dict([(chrom, {"size": size}) for (chrom, size) in data])}
            return jsonify(j)

        elif res_type == "tsv":
            if incl_cum:
                return "\n".join(
                    "{}\t{}\t{}".format(chrom, size, cum) for chrom, size, cum in data
                )
            else:
                return "\n".join("{}\t{}".format(chrom, size) for chrom, size in data)

        else:
            return jsonify({"error": "Unknown response type"}), 500

    @app.route("/api/v1/uids_by_filename/", methods=["GET"])
    def uids_by_filename():
        return jsonify(
            {
                "count": len(TILESETS),
                "results": {i: TILESETS[i] for i in range(len(TILESETS))},
            }
        )

    @app.route("/api/v1/tilesets/", methods=["GET"])
    def tilesets():
        return jsonify(
            {
                "count": len(TILESETS),
                "next": None,
                "previous": None,
                "results": [ts.meta for ts in TILESETS],
            }
        )

    def list_tilesets():
        return TILESETS + list(remote_tilesets.values())

    @app.route("/api/v1/tileset_info/", methods=["GET"])
    def tileset_info():
        uuids = request.args.getlist("d")

        info = {}
        for uuid in uuids:
            ts = next((ts for ts in list_tilesets() if ts.uuid == uuid), None)

            if ts is not None:
                info[uuid] = ts.tileset_info()
            else:
                info[uuid] = {"error": "No such tileset with uid: {}".format(uuid)}

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
            ts = next((ts for ts in list_tilesets() if ts.uuid == uuid), None)
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

        try:
            sh.umount(self.http_directory)
        except Exception as ex:
            pass

        try:
            sh.umount(self.https_directory)
        except Exception as ex:
            pass

        disk_cache_size = 2 ** 25
        disk_cache_dir = self.diskcache_directory
        lru_capacity = 400
        print(
            "self.diskcache_directory",
            self.diskcache_directory,
            op.exists(self.diskcache_directory),
        )

        def start_fuse(directory):
            print("starting fuse")
            fuse = FUSE(
                HttpFs(
                    "http",
                    disk_cache_size=disk_cache_size,
                    disk_cache_dir=self.diskcache_directory,
                    lru_capacity=lru_capacity,
                ),
                directory,
                foreground=False,
            )

        proc = mp.Process(target=start_fuse, args=[self.http_directory])
        proc.start()
        proc.join()

    def teardown(self):
        try:
            sh.umount(self.http_directory)
        except Exception as ex:
            pass

        try:
            sh.umount(self.https_directory)
        except Exception as ex:
            pass


class Server:
    """
    A lightweight HiGlass server.
    """

    # Keep track of the server processes that have been started.
    # So that when someone says 'start', the old ones are terminated
    processes = {}
    diskcache_directory = "/tmp/hgflask/dc"

    def __init__(self, tilesets, port=None, host="localhost", tmp_dir="/tmp/hgflask"):
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
            print("terminating:", puid)
            self.processes[puid].terminate()
            del self.processes[puid]

        self.app = create_app(
            self.tilesets,
            __name__,
            log_file=log_file,
            log_level=log_level,
            file_ids=self.file_ids,
        )

        # we're going to assign a uuid to each server process so that if anything
        # goes wrong, the variable referencing the process doesn't get lost
        uuid = slugid.nice().decode("utf8")
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
            except requests.ConnectionError as err:
                time.sleep(0.2)

    def stop(self):
        """
        Stop this server so that the calling process can exit
        """
        # unsetup_fuse()
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

        print("url:", url)

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


TMP_DIR = "/tmp/higlass-python/"

fuse = FuseProcess(TMP_DIR)
fuse.setup()
