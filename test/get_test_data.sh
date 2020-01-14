#!/usr/bin/env bash
set -e

DATA_DIR=$(dirname "$0")/data

mkdir -p $DATA_DIR

FILES=$(cat <<END
gene_annotations.short.db
Ctcf_WT_allMot.bed.short.bb
END
)

for FILE in $FILES; do
  [ -e data/$FILE ] || wget -P $DATA_DIR https://s3.amazonaws.com/pkerp/public/$FILE
done

