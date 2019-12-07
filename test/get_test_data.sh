#!/usr/bin/env bash
set -e

mkdir -p data

FILES=$(cat <<END
gene_annotations.short.db
Ctcf_WT_allMot.bed.short.bb
END
)

for FILE in $FILES; do
  [ -e data/$FILE ] || wget -P data/ https://s3.amazonaws.com/pkerp/public/$FILE
done

