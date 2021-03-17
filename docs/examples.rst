Examples
########

BAM Files
---------

View sequencing read mappings.

.. code-block:: python

	import higlass
	from higlass.tilesets import Tileset, bam
	from higlass.client import Track, View

	filename = '../data/ont.10K.bam'
	indexfile = '../data/ont.10K.bam.bai'

	bam_ts = bam(filename, indexfile)

	display, server, viewconf = higlass.display(
	    [View([
	        Track('top-axis', height=20),
	        Track(track_type="pileup",
	        	position='top', tileset=bam_ts, height=50 )
	    ], initialXDomain = [
	        0,
	        2000
	      ])]
	)
	display

.. image:: img/jupyter-pileup-no-code.png

Multivec Files
---------------

To view multivec files, we have to load the higlass plugin track. Execute the following code in a cell in the Jupyter notebook you're using.

.. code-block:: javascript

    %%javascript

    require(["https://unpkg.com/higlass-multivec/dist/higlass-multivec"],
        function(hglib) {

    });

Create the multivec and output file:

.. code-block:: python

	from clodius.multivec import create_multivec_multires

	output_file = "/Users/pete/tmp/my_file.multires.hdf5"

	create_multivec_multires(
	    array,
	    [('chr1', chrom_len)],
	    agg=lambda x: np.nansum(x.T.reshape((x.shape[1], -1, 2)), axis=2).T,
	    starting_resolution=1,
	    row_infos = ["match", 'a', 'g', 't'],
	    output_file=output_file,
	    tile_size=256
	)

	ts = multivec(output_file)

Create the viewer:

.. code-block:: python

	import higlass
	from higlass.client import Track, View

	display, server, viewconf = higlass.display(
	    [View([
	        Track('top-axis', height=20),
	        Track(track_type="horizontal-stacked-bar", position='top', tileset=ts, height=50 )
	    ], initialXDomain = [
	        0,
	        1000000
	      ])]
	)
	display
