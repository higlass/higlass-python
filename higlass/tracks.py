import slugid
from higlass.client import Track
from pathlib import Path
from typing import List, Tuple
from numpy import cumsum

import itertools as it
from pathlib import Path

def chromsize_pairs(chromsizes_fn):
    with open(chromsizes_fn, 'r') as f:
        chroms = [l.strip().split('\t') for l in f.readlines()]
        chromnames = [c[0] for c in chroms]
        chromlengths = [int(c[1]) for c in chroms]
    
    return list(zip(chromnames, chromlengths))

def load_chromsizes(chromsizes_fn):
    chrom_names_lengths = chromsize_pairs(chromsizes_fn)
    
    chromnames, chromlengths = zip(*chrom_names_lengths)

    cumlengths = list(it.accumulate(chromlengths))
    # we want the cumlengths to start 0
    cumlengths = [0] + cumlengths[:-1]

    return dict([(name, {
        'name': name,
        'length': length,
        'start': start
    }) for name, length, start in zip(chromnames, chromlengths, cumlengths)])

def beditems(lines: List[Tuple[str, int, int, str, str, str]], chromfile: Path) -> Track:
    """Generate a bedfile track for a list of bed items.
    
    Args:
        lines: A list of bed style lines ([chrom, start, end, name, score, pos])
        
    Returns:
        A higlass Track that can be used with the viewer.
    
    """
    chroms = load_chromsizes(chromfile)

    genome_length = sum(c['length'] for c in chroms.values())
    tileset_info = { 'x': 
        {
            "max_width": genome_length,
            "min_pos": [1],
            "max_pos": [genome_length],
            "max_zoom": 0
        }
    }

    tiles = {
        "x.0.0": [
            {
                "xStart": chroms[l[0]]['start'] + int(l[1]),
                "xEnd": chroms[l[0]]['start'] + int(l[2]),
                "chrOffset": chroms[l[0]]['start'],
                "importance": 0,
                "uid": slugid.nice(),
                "fields": l
            } for l in lines
        ]
    }
    
    return Track(track_type='bedlike', position='top', height=50,
                 data={"type": "local-tiles", "tilesetInfo": tileset_info, "tiles": tiles},
                 options={"annotationHeight": "scaled"})