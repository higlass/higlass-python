from functools import partial
from itertools import count
from io import StringIO
import multiprocess as mp
import cytoolz as toolz
import os.path as op
import platform
import logging
import logging.handlers
import socket
import tempfile
import json
import time
import os
import atexit

from flask import Flask
from flask import request, jsonify

# from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

import requests
import requests_unixsocket
from urllib.request import quote
import slugid
import sh


__all__ = ["Server"]

OS_NAME = platform.system()
OS_TEMPDIR = tempfile.gettempdir()


# Disable annoying logs from werkzeug server
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
log.disabled = True

# The following line is also needed to turn off all debug logs
os.environ["WERKZEUG_RUN_MAIN"] = "true"

requests_unixsocket.monkeypatch()


def create_app(name, tilesets, fuse=None):
    app = Flask(name)
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
                jsonify({"error": "Unknown filetype: {}".format(js["filetype"])}),
                400,
            )

        if fuse is None:
            return jsonify({"error": "httpfs is not available."})

        key = (js["fileUrl"], js["filetype"])
        if key in remote_tilesets:
            ts = remote_tilesets[key]
        else:
            mounted_url = fuse.get_filepath(js["fileUrl"])
            factory = by_filetype[js["filetype"]]
            ts = factory(mounted_url)
            remote_tilesets[key] = ts

        return jsonify({"uid": ts.uuid})

    @app.route("/api/v1/available-chrom-sizes/", methods=["GET"])
    def available_chrom_sizes():
        """
        Get the list of available chromosome size lists. No query parameters.

        """
        results = []
        for ts in tilesets:
            if ts.datatype == "chromsizes":
                results.append(ts.meta)
        return jsonify({"count": len(results), "results": results})

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
        ts = next((ts for ts in _list_tilesets() if ts.uuid == uuid), None)
        if ts is None:
            return jsonify({"error": "Not found"}), 404
        if not hasattr(ts, "chromsizes"):
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
                        chrom: {"size": size, "offset": offset}
                        for chrom, size, offset in data
                    }
                }
            else:
                j = {ts.uuid: {chrom: {"size": size} for chrom, size in data}}
            return jsonify(j)
        elif res_type == "tsv":
            if incl_cum:
                return "\n".join(
                    "{}\t{}\t{}".format(chrom, size, offset)
                    for chrom, size, offset in data
                )
            else:
                return "\n".join("{}\t{}".format(chrom, size) for chrom, size in data)
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
            ts = next((ts for ts in _list_tilesets() if ts.uuid == uuid), None)

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
            ts = next((ts for ts in _list_tilesets() if ts.uuid == uuid), None)
            tiles.extend(ts.tiles(tids))
        data = {tid: tval for tid, tval in tiles}
        return jsonify(data)

    return app


class ServerError(Exception):
    pass


def get_free_socket(sock_dir):
    for p in count():
        sock_file = op.join(sock_dir, str(p))
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            # Check if socket exists and alive
            s.connect(sock_file)
        except OSError:
            # Socket is missing or dead, use it
            try:
                os.remove(sock_file)
            except FileNotFoundError:
                pass
            return p
        # Socket is alive, move on
        s.close()


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

        disk_cache_size = 2**25
        lru_capacity = 400

        def start_fuse(directory, protocol):
            try:
                # this import can cause problems on systems that don't have libfuse
                # installed so let's only try it if absolutely necessary
                from fuse import FUSE

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
                    # allow_other=True
                )
            except RuntimeError as e:
                if str(e) != "1":
                    raise e

        proc1 = mp.Process(target=start_fuse, args=[self.http_directory, "http"])
        proc1.start()
        proc1.join()

        proc2 = mp.Process(target=start_fuse, args=[self.https_directory, "https"])
        proc2.start()
        proc2.join()

    def teardown(self):
        try:
            if OS_NAME == "Darwin":
                sh.umount("HttpFs")
                sh.umount(self.http_directory)
            else:
                sh.fusermount("-uz", self.http_directory)
        except Exception:
            pass

        try:
            if OS_NAME == "Darwin":
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

    Parameters
    ----------
    tilesets : list
        A list of tilesets to serve (see higlass.tilesets)
    host : str, optional
        The host this server is running on. Usually just localhost.
        If starts with unix://, then it's treated as a unix socket. If also ends with a '/',
        then it's treated as a directory of unix sockets, with port being the file name.
    port : int, optional
        The port that this server will run on. If host starts with unix://, then this is the
        file name for the socket inside the base directory.
    name : str, optional
        A name for the Flask app being served. If not provided, a
        unique name will be generated. The app's logger inherits this
        name.
    fuse : bool, optional
        Whether to mount http(s) resources using FUSE.
    tmp_dir : string, optional
        A temporary directory for FUSE to mount the http(s) files and
        for caching.
    log_level: logging.*
        What level to log at
    log_file: str, optional
        Where to write diagnostic log files. Default is to use a
        StringIO stream in memory.
    root_api_address: str, optional
        Root path of the reported api_address, instead of http://{host}:{port}.
        Can be used for redirecting clients to a proxy. Can include {host}, {port}
        and {unix_filename} to use these variables.

    """

    # Keep track of the server processes that have been started.
    # So that when someone says 'start', the old ones are terminated
    processes = {}

    def __init__(
        self,
        tilesets,
        host="localhost",
        port=None,
        name=None,
        fuse=True,
        tmp_dir=OS_TEMPDIR,
        log_level=logging.INFO,
        log_file=None,
        root_api_address=None,
    ):
        self.name = name or __name__.split(".")[0] + "-" + slugid.nice()[:8]
        self.tilesets = tilesets
        self.host = host
        self.port = port
        if fuse:
            self.fuse_process = FuseProcess(op.join(tmp_dir, "higlass-python"))
            self.fuse_process.setup()
        else:
            self.fuse_process = None

        self.app = create_app(self.name, self.tilesets, fuse=self.fuse_process)
        if log_file:
            self.log = None
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=100000, backupCount=1
            )
        else:
            self.log = StringIO()
            handler = logging.StreamHandler(self.log)

        self._root_api_address = root_api_address

        handler.setLevel(log_level)
        self.app.logger.addHandler(handler)

    def start(self, debug=False, **kwargs):
        """
        Start a lightweight higlass server.

        Parameters
        ----------
        debug: bool
            Run the server in debug mode. Default is False.
        kwargs :
            Additional options to pass to app.run

        """
        for puid in list(self.processes.keys()):
            self.processes[puid].terminate()
            del self.processes[puid]

        self._use_unix = self.host.startswith("unix://")
        if not self._use_unix:
            # Use a regular TCP socket, host and port are as usual
            if self.port is None:
                self.port = get_open_port()
            self._unix_filename = None
        else:
            # Use a UNIX socket, host should be a file path prefixed with unix://
            # If host is a directory, make it a filename by joining it with
            # the port field.
            host_no_schema = self.host[7:]
            if host_no_schema[-1] == "/":
                os.makedirs(host_no_schema, mode=0o700, exist_ok=True)
            if op.isdir(host_no_schema):
                if self.port is None:
                    # If no port is given, find a free filename and use that
                    self.port = get_free_socket(host_no_schema)
                self.host = op.join(self.host, str(self.port))
            self._unix_filename = self.host[7:]

        # we're going to assign a uuid to each server process so that if
        # anything goes wrong, the variable referencing the process doesn't get
        # lost
        uuid = slugid.nice()

        target = partial(
            self.app.run,
            debug=debug,
            host=self.host,
            port=self.port,
            threaded=True,
            use_reloader=False,
            **kwargs
        )
        atexit.register(self._unix_cleanup)
        self.processes[uuid] = mp.Process(target=target)
        self.processes[uuid].start()

        self.connected = False
        while not self.connected:
            try:
                url = self._get_url("api/v1")
                r = requests.head(url)
                if r.ok:
                    self.connected = True
            except requests.ConnectionError:
                time.sleep(0.2)

    def _get_url(self, path):
        if self._use_unix:
            host = quote(self._unix_filename, safe="")
            return "http+unix://{}/{}".format(host, path)
        return "http://{}:{}/{}".format(self.host, str(self.port), path)

    def stop(self):
        """
        Stop this server so that the calling process can exit
        """
        if self.fuse_process is not None:
            self.fuse_process.teardown()
        for uuid in self.processes:
            self.processes[uuid].terminate()
        self._unix_cleanup()

    def _unix_cleanup(self):
        if self._use_unix:
            try:
                os.remove(self._unix_filename)
            except FileNotFoundError:
                pass

    def tileset_info(self, uid):
        """
        Return the tileset info for the given tileset
        """
        url = self._get_url("api/v1/tileset_info/?d={uid}".format(uid=uid))

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
        url = self._get_url("api/v1/tiles/?d={tile_id}".format(tile_id=tile_id))

        req = requests.get(url)
        if req.status_code != 200:
            raise ServerError("Error fetching tile:", req.content)

        content = json.loads(req.content)
        return content[tile_id]

    def chromsizes(self, uid):
        """
        Return the chromosome sizes from the given filename
        """
        url = self._get_url("api/v1/chrom-sizes/?id={uid}".format(uid=uid))

        req = requests.get(url)
        if req.status_code != 200:
            raise ServerError("Error fetching chromsizes:", req.content)

        return req.content

    @property
    def api_address(self):
        if self._root_api_address is None:
            return self._get_url("api/v1")
        root = self._root_api_address.format(
            host=self.host, port=self.port, unix_filename=self._unix_filename or ""
        )
        return "{}/api/v1".format(root)
