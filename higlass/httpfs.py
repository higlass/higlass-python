#!/usr/bin/env python
from errno import EIO, ENOENT
from stat import S_IFDIR, S_IFREG
from threading import Timer
from time import time
import functools as ft
import logging
import os
import sys

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import requests

BLOCK_SIZE = 2 ** 16

CLEANUP_INTERVAL = 60
CLEANUP_EXPIRED = 60

DISK_CACHE_SIZE_ENV = 'HTTPFS_DISK_CACHE_SIZE'
DISK_CACHE_DIR_ENV = 'HTTPFS_DISK_CACHE_DIR'

import collections
import diskcache as dc

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = collections.OrderedDict()

    def __getitem__(self, key):
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def __setitem__(self, key, value):
        try:
            self.cache.pop(key)
        except KeyError:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
        self.cache[key] = value

    def __contains__(self, key):
        return key in self.cache

    def __len__(self):
        return len(self.cache)


class HttpFs(LoggingMixIn, Operations):
    """
    A read only http/https/ftp filesystem.

    """
    def __init__(self, _schema, disk_cache_size=2**30, disk_cache_dir='/tmp/xx', lru_capacity=400):
        self.schema = _schema
        self.files = dict()
        self.cleanup_thread = self._generate_cleanup_thread(start=False)
        self.lru_cache = LRUCache(capacity=lru_capacity)

        print('dc_dir', disk_cache_dir, disk_cache_size)
        self.disk_cache = dc.Cache(disk_cache_dir, disk_cache_size)

        self.lru_hits = 0
        self.lru_misses = 0

        self.disk_hits = 0
        self.disk_misses = 0

    def init(self, path):
        self.cleanup_thread.start()

    def getattr(self, path, fh=None):
        logging.info("attr path: {}".format(path))
        
        if path in self.files:
            return self.files[path]['attr']

        elif path.endswith('..'):
            url = '{}:/{}'.format(self.schema, path[:-2])
            
            logging.info("attr url: {}".format(url))
            head = requests.head(url, allow_redirects=True)
            logging.info("head: {}".format(head.headers))
            logging.info("status_code: {}".format(head.status_code))

            attr = dict(
                st_mode=(S_IFREG | 0o644), 
                st_nlink=1,
                st_size=int(head.headers['Content-Length']),
                st_ctime=time(), 
                st_mtime=time(),
                st_atime=time())
            
            self.files[path] = dict(
                time=time(), 
                attr=attr)
            return attr

        else:
            return dict(st_mode=(S_IFDIR | 0o555), st_nlink=2)

    def read(self, path, size, offset, fh):
        print("read", offset, size)
        #logging.info("read path: {}".format(path))
        if path in self.files:
            url = '{}:/{}'.format(self.schema, path[:-2])
            logging.info("read url: {}".format(url))
            logging.info("offset: {} - {} block: {}".format(offset, offset + size - 1, offset // 2 ** 18))
            output = [0 for i in range(size)]

            t1 = time()

            # nothing fetched yet
            last_fetched = -1
            curr_start = offset

            while last_fetched < offset + size:
                #print('curr_start', curr_start)
                block_num = curr_start // BLOCK_SIZE
                block_start = BLOCK_SIZE * (curr_start // BLOCK_SIZE)

                #print("block_num:", block_num, "block_start:", block_start)
                block_data = self.get_block(url, block_num)

                data_start = curr_start - (curr_start // BLOCK_SIZE) * BLOCK_SIZE
                data_end = min(BLOCK_SIZE, offset + size - block_start)

                data = block_data[data_start:data_end]

                #print("data_start:", data_start, data_end, data_end - data_start)
                for (j,d) in enumerate(data):
                    output[curr_start-offset+j] = d

                last_fetched = curr_start + (data_end - data_start)
                curr_start += (data_end - data_start)

            t2 = time()

            # logging.info("sending request")
            # logging.info(url)
            # logging.info(headers)
            logging.info("lru hits: {} lru misses: {} disk hits: {} disk misses: {}"
                    .format(self.lru_hits, self.lru_misses, self.disk_hits, self.disk_misses))

            self.files[path]['time'] = t2  # extend life of cache entry

            logging.info("time: {:.2f}".format(t2 - t1))
            return bytes(output)
            
        else:
            logging.info("file not found")
            raise FuseOSError(EIO)

    def destroy(self, path):
        self.cleanup_thread.cancel()

    def cleanup(self):
        now = time()
        num_files_before = len(self.files)
        self.files = {
            k: v for k, v in self.files.items() 
                if now - v['time'] < CLEANUP_EXPIRED
        }
        num_files_after = len(self.files)
        if num_files_before != num_files_after:
            logging.info(
                'Truncated cache from {} to {} files'.format(
                    num_files_before, num_files_after))
        self.cleanup_thread = self._generate_cleanup_thread()

    def _generate_cleanup_thread(self, start=True):
        cleanup_thread = Timer(CLEANUP_INTERVAL, self.cleanup)
        cleanup_thread.daemon = True
        if start:
            cleanup_thread.start()
        return cleanup_thread

    def get_block(self, url, block_num):
        '''
        Get a data block from a URL. Blocks are 256K bytes in size

        Parameters:
        -----------
        url: string
            The url of the file we want to retrieve a block from
        block_num: int
            The # of the 256K'th block of this file
        '''
        cache_key=  "{}.{}".format(url, block_num)
        cache = self.disk_cache

        if cache_key in self.lru_cache:
            self.lru_hits += 1
            return self.lru_cache[cache_key]
        else:
            self.lru_misses += 1

            if cache_key in self.disk_cache:
                self.disk_hits += 1
                block_data = self.disk_cache[cache_key]
                self.lru_cache[cache_key] = block_data
                return block_data
            else:
                self.disk_misses += 1
                block_start = block_num * BLOCK_SIZE
                
                headers = {
                    'Range': 'bytes={}-{}'.format(block_start, block_start + BLOCK_SIZE - 1)
                }
                print('sending request:', headers['Range'])
                r = requests.get(url, headers=headers)
                logging.info(r)
                block_data = r.content
                logging.info(r.content)
                self.lru_cache[cache_key] = block_data
                self.disk_cache[cache_key] = block_data

        return block_data


def main():
    import argparse
    parser = argparse.ArgumentParser(description="""
    usage: httpfs <mountpoint> <http|https|ftp>
""")
    parser.add_argument('mountpoint')
    parser.add_argument('schema')
    parser.add_argument(
        '-f', '--foreground', 
        action='store_true', 
        default=False,
    	help='Run in the foreground')

    parser.add_argument(
        '--disk-cache-size', default=2**30, type=int)
    parser.add_argument(
        '--disk-cache-dir', default='/tmp/xx')
    parser.add_argument(
        '--lru-capacity', default=400, type=int)

    args = vars(parser.parse_args())

    logging.getLogger().setLevel(logging.INFO)
    logging.info("starting:")
    logging.info("foreground: {}".format(args['foreground']))
    
    fuse = FUSE(
        HttpFs(args['schema'],
               disk_cache_size=args['disk_cache_size'],
               disk_cache_dir=args['disk_cache_dir'],
               lru_capacity=args['lru_capacity']
            ), 
        args['mountpoint'], 
        foreground=args['foreground']
    )


if __name__ == '__main__':
    main()

