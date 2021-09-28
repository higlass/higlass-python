import itertools as it
from typing import Tuple

def load_chromsizes(chrom_names_lengths):
    chromnames, chromlengths = zip(*chrom_names_lengths)

    cumlengths = list(it.accumulate(chromlengths))
    # we want the cumlengths to start 0
    cumlengths = [0] + cumlengths[:-1]

    return dict(
        [
            (name, {"name": name, "length": length, "start": start})
            for name, length, start in zip(chromnames, chromlengths, cumlengths)
        ]
    )

def chromsize_pairs(chromsizes_fn: str):
    with open(chromsizes_fn, "r") as f:
        chroms = [l.strip().split("\t") for l in f.readlines()]
        chromnames = [c[0] for c in chroms]
        chromlengths = [int(c[1]) for c in chroms]

    return list(zip(chromnames, chromlengths))

def chrom_to_abs(chroms_dict: dict, chrom: str, pos: int) -> int:
    """Convert a chromosome position to an absolute position."""
    return chroms_dict[chrom]['start'] + pos

def chrom_pos_region(
    chroms_dict: dict, chrom: str, pos: int, padding: int=100
) -> Tuple[int, int]:
    center = chrom_to_abs(chroms_dict, chrom, pos)
    return (center - padding, center+padding)

def abs_to_chrom(chroms_dict: dict, abs_pos: int) -> Tuple[str, int]:
    """Convert an absolute genomic position to a chr, pos tuple.

    Assumes 0-based coordinates.

    Raises:
        ValueError if the absolute position is outside the bounds of
        this genome.
    """
    for chrom in chroms_dict.values():
        if chrom['start'] <= abs_pos and abs_pos < chrom['start'] + chrom['length']:
            return (chrom['name'], abs_pos - chrom['start'])

    raise ValueError("The given position is outside the range of genome.")
