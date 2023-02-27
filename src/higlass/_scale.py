from __future__ import annotations

import itertools
from bisect import bisect_right
from typing import Iterable, Tuple

GenomicPosition = Tuple[str, int]


class Scale:
    """
    A bidirectional mapping between a composite genomic coordinate system and
    a partition of that coordinate system into a sequence of bins.

    The partition is a sequence of bins of a fixed size, with the exception of
    the last bin in each chromosome, which may be smaller than the fixed size.
    Bins do not cross chromosome boundaries. The scale provides a mapping from
    a genomic coordinate to the index of the bin in which it falls, and a
    mapping from a bin index to the genomic coordinate of the bin's start.

    Parameters
    ----------
    chromsizes : dict | list[tuple]
        A dictionary of chromosome names and lengths or a list of tuples
        of chromosome names and lengths.
    binsize : int, optional
        The size of each bin in the partition in bp (default: 1).

    Notes
    -----
    The genomic coordinates are 0-based and the bins of the partition are
    half-open intervals, i.e. the start coordinate of a bin is included in the
    bin, but the end is not.
    """

    def __init__(
        self,
        chromsizes: dict[str, int] | Iterable[tuple[str, int]],
        binsize: int = 1,
    ):
        chromsizes = dict(chromsizes)
        names, lengths = zip(*chromsizes.items())
        lengths_binned = [(length + binsize - 1) // binsize for length in lengths]
        chrom_offsets = list(itertools.accumulate(lengths_binned, initial=0))
        self._chrom_names = names
        self._chrom_offsets = chrom_offsets
        self._chrom_lengths_map = chromsizes
        self._chrom_offsets_map = dict(zip(names, chrom_offsets[:-1]))
        self.n_bins = chrom_offsets[-1]
        self.binsize = binsize

    def offset(self, gpos: GenomicPosition) -> int:
        """
        Returns the index of the bin in which the given genomic position falls.
        """
        chrom, pos = gpos
        chrom_offset = self._chrom_offsets_map[chrom]
        clen = self._chrom_lengths_map[chrom]
        if pos < 0:
            pos = 0
        if pos >= clen:
            pos = clen - 1
        return chrom_offset + pos // self.binsize

    def invert(self, offset: int) -> GenomicPosition:
        """
        Returns the genomic position of the start of the bin at the given index.
        """
        offset = max(0, min(offset, self.n_bins - 1))
        i = bisect_right(self._chrom_offsets, offset)
        chrom = self._chrom_names[i - 1]
        rel_offset = offset - self._chrom_offsets[i - 1]
        return chrom, rel_offset * self.binsize
