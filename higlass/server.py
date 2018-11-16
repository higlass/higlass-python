__all__ = ['start']

# -*- coding: utf-8 -*-
import cytoolz as toolz
import functools as ft
import json
import requests
import slugid
import multiprocessing as mp
import sh

import hgtiles.bed2ddb as hgb2
import hgtiles.cooler as hgco
import hgtiles.hitile as hghi
import hgtiles.bigwig as hgbi
import hgtiles.files as hgfi

import os
import os.path as op
import sys
import multiprocessing as mp
import time

from flask import Flask
from flask import request, jsonify
#from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS

from fuse import FUSE


def create_app(tilesets):
    app = Flask(__name__)
    CORS(app)

    TILESETS = tilesets

    #############
    ### VIEWS ###
    #############


    @app.route('/api/v1/')
    def hello():
        return("Hello World!")


    '''
    CHROMSIZES = {
        'hg19': {
            "chr1": {"size": 249250621}, 
            "chr2": {"size": 243199373}, 
            "chr3": {"size": 198022430}, 
            "chr4": {"size": 191154276}, 
            "chr5": {"size": 180915260}, 
            "chr6": {"size": 171115067}, 
            "chr7": {"size": 159138663}, 
            "chr8": {"size": 146364022}, 
            "chr9": {"size": 141213431}, 
            "chr10": {"size": 135534747}, 
            "chr11": {"size": 135006516}, 
            "chr12": {"size": 133851895}, 
            "chr13": {"size": 115169878}, 
            "chr14": {"size": 107349540}, 
            "chr15": {"size": 102531392}, 
            "chr16": {"size": 90354753}, 
            "chr17": {"size": 81195210}, 
            "chr18": {"size": 78077248}, 
            "chr19": {"size": 59128983}, 
            "chr20": {"size": 63025520}, 
            "chr21": {"size": 48129895}, 
            "chr22": {"size": 51304566}, 
            "chrX": {"size": 155270560}, 
            "chrY": {"size": 59373566}, 
            "chrM": {"size": 16571},
        },
    }

    @app.route('/api/v1/available-chrom-sizes/', methods=['GET'])
    def available_chrom_sizes():
        return jsonify({
            "count": len(CHROMSIZES), 
            "results": {i: CHROMSIZES[i] for i in range(len(CHROMSIZES))}
        })
    '''


    @app.route('/api/v1/chrom-sizes/', methods=['GET'])
    def chrom_sizes():
        uuid = request.args.get('id', None)
        res_type = request.args.get('type', 'tsv')
        incl_cum = request.args.get('cum', False)

        ts = next((ts for ts in TILESETS if ts.uuid == uuid), None)

        if ts is None:
            return jsonify({"error": "Not found"}), 404
        
        data = ts.chromsizes()
        
        new_data = []
        
        if incl_cum:
            cum = 0
            for (chrom, size) in data:
                new_data += [(chrom, size, cum)]
                cum += size 

            for chrom in data.keys():   # dictionaries in py3.6+ are ordered!
                data[chrom]['offset'] = cum
                cum += data[chrom]['size']

        if res_type == 'json':
            # should return
            # { uuid: {
            #   'chr1': {'size': 2343, 'offset': 0},
            #
            if incl_cum:
                j = {
                        ts.uuid: dict([(chrom, { 'size': size, 'offset': offset }) for 
                            (chrom, size, offset) in data])
                    }
            else:
                j = {
                        ts.uuid: dict([(chrom, { 'size': size }) for 
                            (chrom, size) in data])
                    }
            return jsonify(j)

        elif res_type == 'tsv':
            if incl_cum:
               return '\n'.join('{}\t{}\t{}'.format(chrom, size, cum)
                       for chrom, size, cum in data)
            else:
                return '\n'.join('{}\t{}'.format(chrom, size)
                    for chrom, size in data)

        else:
            return jsonify({"error": "Unknown response type"}), 500


    @app.route('/api/v1/uids_by_filename/', methods=['GET'])
    def uids_by_filename():
        return jsonify({
            "count": len(TILESETS), 
            "results": {i: TILESETS[i] for i in range(len(TILESETS))}
        })


    @app.route('/api/v1/tilesets/', methods=['GET'])
    def tilesets():
        return jsonify({
            "count": len(TILESETS),
            "next": None,
            "previous": None,
            "results": TILESETS,
        })

    def get_filepath(tileset_def):
        '''
        Get the filepath from a tileset definition

        Parameters
        ----------
        tileset_def: { 'filepath': ..., 'uid': ..., 'filetype': ...}
            The tileset definition     
        returns: string
            The filepath, either as specified in the tileset_def or
            None
        '''
        if 'filepath' in tileset_def:
            filepath = tileset_def['filepath']
            
            if filepath[:7] == 'http://':
                filepath = http_directory + '//' + filepath[5:] + ".."
            if filepath[:8] == 'https://':
                filepath = https_directory + '//' + filepath[6:] + ".."
            
            return filepath

        return None

    def get_filetype(tileset_def):
        '''
        Get the filetype for the given dataset.

        Parameters
        ----------
        tileset_def: { 'filepath': ..., 'uid': ..., 'filetype': ...}
            The tileset definition     
        returns: string
            The filetype, either as specified in the tileset_def or
            inferred
        '''
        if 'filetype' in tileset_def:
            return tileset_def['filetype']

        if 'filepath' not in tileset_def:
            return None

        return hgfi.infer_filetype(tileset_def['filepath'])

    @app.route('/api/v1/tileset_info/', methods=['GET'])
    def tileset_info():
        uuids = request.args.getlist("d")

        info = {}
        for uuid in uuids:
            ts = next((ts for ts in TILESETS if ts.uuid == uuid), None)
            
            if ts is not None:
                info[uuid] = ts.tileset_info()
            else:
                info[uuid] = {
                    'error': 'No such tileset with uid: {}'.format(uuid)
                }

        return jsonify(info)


    @app.route('/api/v1/tiles/', methods=['GET'])
    def tiles():
        tids_requested = set(request.args.getlist("d"))
        
        if not tids_requested:
            return jsonify({'error': 'No tiles requested'}), 400
        
        extract_uuid = lambda tid: tid.split('.')[0]
        uuids_to_tids = toolz.groupby(extract_uuid, tids_requested)
        
        tiles = []
        for uuid, tids in uuids_to_tids.items():
            ts = next((ts for ts in TILESETS if ts.uuid == uuid), None)
            tiles.extend(ts.tiles(tids))
        data = {tid: tval for tid, tval in tiles}
        return jsonify(data)

    # if __name__ == '__main__':
    #     app.run(debug=True, port=5000)

        # import threading
        # from functools import partial
        # t = threading.Thread(target=partial(app.run, debug=True, port=5000))

    return app

def get_open_port():
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port

class RunningServer():
    def __init__(self, port, process, host='localhost'):
        '''
        Maintain a reference to a running higlass server

        Parameters:
        ----------
        port: int
            The port that this server is running on
        process: Popen.process
            The process running the server
        '''
        self.host = 'localhost'
        self.port = port
        self.process = process

    def tileset_info(self, uid):
        '''
        Return the tileset info for the given tileset
        '''
        url = 'http://localhost:{port}/api/v1/tileset_info/?d={uid}'.format(
                port=self.port, uid=uid)

        req = requests.get(url)
        if req.status_code != 200:
            raise Exception('Error fetching tileset_info:', req.content)

        content = json.loads(req.content)
        return content[uid]

    def tiles(self, uid, z, x, y=None):
        '''
        Return tiles from the specified dataset (uid) at
        the given position (z,x,[u])
        '''
        tile_id ='{uid}.{z}.{x}'.format(uid=uid, z=z, x=x)
        if y is not None:
            tile_id += '.{y}'.format(y=y)
        url = 'http://localhost:{port}/api/v1/tiles/?d={tile_id}'.format(
                port=self.port, tile_id=tile_id)

        req = requests.get(url)
        if req.status_code != 200:
            raise Exception('Error fetching tile:', req.content)

        content = json.loads(req.content)
        return content[tile_id]

    def chromsizes(self, uid):
        '''
        Return the chromosome sizes from the given filename
        '''
        url = 'http://localhost:{port}/api/v1/chrom-sizes/?id={uid}'.format(
                port=self.port,
                uid=uid)

        req = requests.get(url)
        if req.status_code != 200:
            raise Exception('Error fetching chromsizes:', req.content)

        return req.content

    def stop(self):
        '''
        Stop this server so that the calling process can exit
        '''
        # unsetup_fuse()

        self.process.terminate()

    @property
    def api_address(self):
        return 'http://{}:{}/api/v1'.format(self.host, self.port)

'''
Keep track of the server processes that have been started.
So that when someone says 'start', the old ones are terminated
'''
processes = {}

http_directory = '/tmp/hgflask/http'
https_directory = '/tmp/hgflask/https'
diskcache_directory = '/tmp/hgflask/dc'

def unsetup_fuse():
    global http_directory 
    global https_directory

    try:
        sh.umount(http_directory)
    except Exception as ex:
        pass

    try:
        sh.umount(https_directory)
    except Exception as ex:
        pass


def setup_fuse(tmp_dir):
    '''
    Set up filesystem in user space for http and https 
    so that we can retrieve tiles from remote sources.
    
    Parameters 
    ----------
    tmp_dir: string 
        The temporary directory where to create the 
        http and https directories 
    '''
    import hgflask.httpfs as hht

    global processes
    global http_directory 
    global https_directory

    http_directory = op.join(tmp_dir, 'http')
    https_directory = op.join(tmp_dir, 'https')
    diskcache_directory = op.join(tmp_dir, 'dc')

    if not op.exists(http_directory):
        os.makedirs(http_directory)
    if not op.exists(https_directory):
        os.makedirs(https_directory)
    if not op.exists(diskcache_directory):
        os.makedirs(diskcache_directory)

    try:
        sh.umount(http_directory)
    except Exception as ex:
        pass

    try:
        sh.umount(https_directory)
    except Exception as ex:
        pass

    disk_cache_size = 2**25
    disk_cache_dir = diskcache_directory
    lru_capacity = 400
    print("diskcache_directory", diskcache_directory, op.exists(diskcache_directory))

    def start_fuse(directory):
        print("starting fuse")
        fuse = FUSE(
            hht.HttpFs('http',
                   disk_cache_size=disk_cache_size,
                   disk_cache_dir=diskcache_directory,
                   lru_capacity=lru_capacity,
                ), 
            directory,
            foreground=False
        )

    thread = mp.Process(target = start_fuse, args=[http_directory])
    thread.start()
    thread.join()
    # start_fuse(http_directory)

    '''
    fuse = FUSE(
        HttpFs('https',
               disk_cache_size=disk_cache_size,
               disk_cache_dir=disk_cache_dir,
               lru_capacity=lru_capacity,
            ), 
        https_directory,
        foreground=False
    )
    '''


def start(tilesets, port=None, tmp_dir='/tmp/hgflask'):
    '''
    Start the hgflask server. If a port is not specified, an open port 
    will be automatically selected.

    Parameters
    ----------
    tilesets: object
        The list of tilesets to serve. For example:

        .. code-block:: python

            import hgflask.tilesets as hfti

            tilesets = [
                hfti.cooler('mycooler.cool',
                hfti.bigwig('mybigwig.bigWig',
            ]
    port: int
        The port to start this server on. If it is None, a port
        will automatically be assigned.
    tmp_dir: string 
        A temporary directory to be used for mounting http files 
        (experimental)
    '''
    # fuse = setup_fuse(tmp_dir)
    to_delete = []

    # simmple integrity check
    """
    for tileset in tilesets:
        try:
            if ('filepath' not in tileset 
                    and ('filetype' in tileset and tileset['filetype'] not in filetype_handlers)
                    and 'handlers' not in tileset):
                print("WARNING: tileset missing filepath or filetype handler", tileset)
        except TypeError:
            print("ERROR: Are you sure the list of tilesets is a list?")
            raise
        
        if 'filepath' in tileset:
            tileset['filepath'] = op.expanduser(tileset['filepath'])
    """


    for puid in processes:
        print("terminating:", puid)
        processes[puid].terminate()
        to_delete += [puid]

    for puid in to_delete:
        del processes[puid]

    # we're going to assign a uuid to each server process so that if anything
    # goes wrong, the variable referencing the process doesn't get lost
    app = create_app(tilesets=tilesets)# we're going to assign a uuid to each server process so that if anything
    # goes wrong, the variable referencing the process doesn't get lost
    app = create_app(tilesets=tilesets)

    port=get_open_port() if port is None else port

    uuid = slugid.nice().decode('utf8')
    processes[uuid] = mp.Process(
        target=ft.partial(app.run, 
                          threaded=True,
                          debug=True, 
                          port=port, 
                          host='0.0.0.0',
                          use_reloader=False))

    processes[uuid].start()

    connected = False
    while not connected:
        try:
            ret = requests.get('http://localhost:{}/api/v1/tileset_info/?d=a'.format(port))
            print('ret:', ret.status_code, ret.content)
            connected = True
        except Exception as err:
            print('sleeping')
            time.sleep(.2)
            pass
    print("returning")

    return RunningServer(port, processes[uuid])

