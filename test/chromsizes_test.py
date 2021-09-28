import pytest

from higlass.chromsizes import load_chromsizes, chrom_to_abs, abs_to_chrom

def test_chrom_to_abs():
	chroms_dict = load_chromsizes([('chr1', 2000), ('chr2', 1000)])

	assert chrom_to_abs(chroms_dict, 'chr1', 10) == 10
	assert chrom_to_abs(chroms_dict, 'chr2', 10) == 2010

def test_abs_to_chrom():
	chroms_dict = load_chromsizes([('chr1', 2000), ('chr2', 1000)])

	assert abs_to_chrom(chroms_dict, 10) == ('chr1', 10)
	assert abs_to_chrom(chroms_dict, 2010) == ('chr2', 10)

	with pytest.raises(ValueError):
		abs_to_chrom(chroms_dict, -1)


	with pytest.raises(ValueError):
		abs_to_chrom(chroms_dict, 3000)