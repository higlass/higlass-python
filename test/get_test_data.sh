#!/usr/bin/env bash
set -e

mkdir -p data

FILES=$(cat <<END
Dixon2012-J1-NcoI-R1-filtered.100kb.multires.cool
wgEncodeCaltechRnaSeqHuvecR1x75dTh1014IlnaPlusSignalRep2.bigWig
chromSizes_hg19.tsv
chromSizes_hg19_reordered.tsv
int_matrices.hdf5
gene_annotations.short.db
Ctcf_WT_allMot.bed.short.bb
END
)

for FILE in $FILES; do
  [ -e data/$FILE ] || wget -P data/ https://s3.amazonaws.com/pkerp/public/$FILE
done

