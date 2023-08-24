Examples
########

Passing in an auth token
------------------------

If the source higlass server requires authentication, an auth token
can be passed in to the `Authorization` header of the request. To do
this, the viewer needs to be instantiated as a widget with the
contents of the authorization header passed in.

.. code-block:: python

    from higlass import view

    v1 = view(...)
    v1.widget(authToken=f"Bearer <my_token>")

Synchronizing location, zoom and value scales
---------------------------------------------

To synchronize, the locations, zoom levels and value scales, use the provided
``hg.lock`` to create a lock object and then register the given lock for the
visualization with ``hg.Viewconf.locks()``.

.. code-block:: python

    import higlass as hg

    ts = hg.remote(
      uid='CQMd6V_cRw6iCI_-Unl3PQ',
      server="http://higlass.io/api/v1/",
    )

    # the entire viewport has a width of 12 so a width of 6 for
    # each view means they take up half the width
    view1 = hg.view(
        ts.track("chromosome-labels"),
        ts.track("heatmap"),
        width=6,
    )

    view2 = hg.view(
        ts.track("chromosome-labels"),
        ts.track("heatmap"),
        width=6,
    )

    lock = hg.lock(view1, view2)

    (view1 | view2).locks(lock)


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


Create the viewer:

.. code-block:: python

    import higlass as hg

    ts = multivec(output_file)
    view = hg.view(
        hg.track("top-axis", height=20),
        ts.track("horizontal-stacked-bar", height=50),
    )
    view.domain(x=[0, 1000000])
