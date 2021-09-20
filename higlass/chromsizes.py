import itertools as it

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