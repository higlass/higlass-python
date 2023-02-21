Getting Started
###############

**higlass-python** is a Python interface for HiGlass. It simplifies authoring
HiGlass view configs and offers additional features to load and visualize local
datasets as well as extend HiGlass server functionality.


Key features
------------

- Author validated HiGlass view configs with a simplified API
- Render HiGlass visualizations as standalone HTML or interactive Jupyter Widgets
- Load local, remote, and in-memory datasets via a light-weight, background HiGlass server
- Extend local HiGlass server with custom tilesets


Example
-------

.. code-block:: bash

    pip install higlass-python


.. code-block:: python

    import higlass as hg

    # Remote data source (tileset)
    tileset1 = hg.remote(
        uid="CQMd6V_cRw6iCI_-Unl3PQ",
        server="https://higlass.io/api/v1/",
        name="Rao et al. (2014) GM12878 MboI (allreps) 1kb",
    )

    # Local tileset
    tileset2 = hg.cooler("../data/dataset.mcool")

    # Create a `hg.HeatmapTrack` for each tileset
    track1 = tileset1.track("heatmap")
    track2 = tileset2.track("heatmap")

    # Create two independent `hg.View`s, one for each heatmap
    view1 = hg.view(track1, width=6)
    view2 = hg.view(track2, width=6)

    # Lock zoom & location for each `View`
    view_lock = hg.lock(view1, view2)

    # Concatenate views horizontally and apply synchronization lock
    (view1 | view2).locks(view_lock)


.. image:: https://user-images.githubusercontent.com/24403730/159050305-e6a48f03-fba1-4ff7-8eee-2e9c5c40ef88.gif

Whats going on here:

- ``tileset1`` defines a remote tileset (data source), pointing to an exisiting
  HiGlass server.
- ``tileset2`` defines a local tileset, configuring a background HiGlass server
  to serve tiles from the included cooler file.
- ``track1`` and ``track2`` specify separate ``hg.HeatmapTrack`` objects derived
  from the above tilesets, which are inserted into two separate views (``view1`` and ``view2`` respectively).
- ``view_lock`` is an ``hg.Lock`` instance, defining an abstract link between the two views.
- Finally, the two views are concatenated horizontally into a single ``hg.Viewconf`` (via the ``|`` operator),
  and lock is used to sync the zoom and location.


Simplest use case
------------------

The simplest way to instantiate a HiGlass instance to create a View with an axis Track:

.. code-block:: python

   import higlass as hg

   hg.view(hg.track("top-axis"))


The ``hg.track`` and ``hg.view`` utilties provide a flexibile API for creating and composing
multiple HiGlass Views and Tracks. The ``hg.view`` utility accepts one or more tracks as
positional arguments, and view-level properties are specified via keyword-only arguments.

.. code-block:: python

   import higlass as hg

   hg.view(
       hg.track("top-axis"),
       hg.track("left-axis"),
       width=6,
   )

By default, track positions are are inferred via track type but may be overriden or
provided explicitly as a tuple of ``(hg.Track, "top" | "right" | "bottom" | "left")``.


.. code-block:: python

   import higlass as hg

   hg.view(
       (hg.track("top-axis"), "top"),
       (hg.track("left-axis"), "left"),
       width=6,
   )


Creating a viewconf
-------------------

At it's core, **higlass-python** is a Python interface for authoring
and composing validated HiGlass view configs. This core API can
be used outside of Jupyter notebooks to load or export HiGlass
configurations without any rendering. For example, creating and
exporting a view config as JSON:

.. code-block:: python

  import higlass as hg

  pileup_track = hg.track("pileup").properties(
      data={"type": "bam", "url": "my_bam"},
  ).opts(
      axisPositionHorizontal="right",
  )
  view = hg.view(hg.track("top-axis"), (pileup_track, "top"))
  view.viewconf().json() # or .dict() for a Python dict

  # {
  #   "editable": true,
  #   "viewEditable": true,
  #   "tracksEditable": true,
  #   "views": [
  #     {
  #       "layout": { "x": 0, "y": 0, "w": 12, "h": 6 },
  #       "tracks": {
  #         "top": [
  #           {
  #             "type": "top-axis",
  #             "uid": "5f8433fc-9b7a-48a2-b4c3-bccddf8a0bee"
  #           },
  #           {
  #             "type": "pileup",
  #             "uid": "68405ebc-08b2-469a-ab96-ea7925a39ae2",
  #             "options": {
  #               "axisPositionHorizontal": "right"
  #             },
  #             "data": {
  #               "type": "bam",
  #               "url": "my_bam"
  #             }
  #           }
  #         ]
  #       },
  #       "uid": "2d774b94-fc5d-49c2-9c51-bbad9fa6e73f",
  #       "zoomLimits": [1, null]
  #     }
  #   ]
  # }

or loading an existing view config via URL to access a sub-track:

.. code-block:: python

  import higlass as hg

  viewconf = hg.Viewconf.from_url("https://higlass.io/api/v1?d=default")
  viewconf.views[0].tracks.top[0].json()

  # {
  #   "tilesetUid": "OHJakQICQD6gTD7skx4EWA",
  #   "server": "//higlass.io/api/v1",
  #   "type": "horizontal-gene-annotations",
  #   "uid": "OHJakQICQD6gTD7skx4EWA",
  #   "height": 60,
  #   "options": {
  #     "name": "Gene Annotations (hg19)"
  #   }
  # }


View extent
-----------

The extent of a view can be set using the ``hg.View.domain()`` method,
either in 1D:


.. code-block:: python

   import higlass as hg

   view = hg.view(hg.track("top-axis")).domain(x=[0, 1e7])


or 2D:


.. code-block:: python

   import higlass as hg

   view = hg.view(hg.track("heatmap")).domain(x=[0, 1e7], y=[0, 1e7])


Track Types
-----------

A list of available track types can be found in the `documentation for HiGlass
<https://docs.higlass.io/track_types.html>`_. Based on the data type, we can
sometimes provide a recommended track type as well as a recommended position.

.. code-block:: python

  import higlass.client as hgc
  track_type, position = hgc.datatype_to_tracktype(datatype)


Combining Tracks
----------------

Tracks can be combined by overlaying them on top of each other or by performing operations with them.

Overlaying tracks
^^^^^^^^^^^^^^^^^

Two tracks can be overlayed by using the ``+`` operator:

.. code-block:: python

  view=View([Track('top-axis') +
         Track('horizontal-bar',
              server='//higlass.io/api/v1',
              tilesetUid='F2vbUeqhS86XkxuO1j2rPA')
        ], initialXDomain=[0,1e9])

Another way to express this is to pass in a list of tracks
as if it were a single track:

.. code-block:: python

  view=View([[Track('top-axis'),
         Track('horizontal-bar',
              server='//higlass.io/api/v1',
              tilesetUid='F2vbUeqhS86XkxuO1j2rPA')
        ]], initialXDomain=[0,1e9])

Multiple Views
--------------

Multiple views can be instantiated much like single views. They are positioned
a on grid that is 12 units wide and an arbitrary number of units high. To
create two side by side views, set both to be 6 units wide and one on the
right to be at x position 6:

.. code-block:: python

  import higlass
  from higlass.client import Track, View

  view1 = View([Track(type='top-axis')], x=0, width=6)
  view2 = View([Track(type='top-axis')], x=6, width=6)

  display, server, viewconf = higlass.display([view1, view2])
  display

.. image:: img/two-simple-views.png

Synchronization
---------------

Views and track can be synchronized by location, zoom level and values scales.

Zoom and Location locks
^^^^^^^^^^^^^^^^^^^^^^^

Location locks ensure that when one view is panned, all synchronized views pan
with it. Zoom locks do the same with zoom level. Both can be instantiated by
passing lists of views to lock to ``higlass.display``. Each set of locked
views will scroll or zoom (or both) together:

.. code-block:: python

  display, server, viewconf = higlass.display(
    [view1, view2],
    location_syncs=[[view1, view2]],
    zoom_syncs=[[view1, view2]])

Viewport Projection
-------------------

Viewport projections can be instantiated like other tracks. It is created with
a reference to the view we wish to track and combined with another track where
it will be overlayed.

.. code-block:: python

    from higlass.client import ViewportProjection

    view1 = View([
        Track(type='top-axis'),
    ], initialXDomain=[0,1e7])

    projection = ViewportProjection(view1)

    view2 = View([
        Track(type='top-axis') + projection,
    ], initialXDomain=[0,2e7])

Note that `ViewportProjection` tracks always need to be paired with other non-
ViewportProjection tracks. Multiple ViewportProjection tracks can, however, be
combined, as long as they are associated with regular tracks.

Combined tracks can also be created by passing a list of tracks
as if it were a track itself to a ``View``.

.. code-block:: python

    view2 = View([
      [ Track(type='top-axis'), projection ]
    ], initialXDomain=[0,2e7])

Dataset Arithmetic
-------------------

HiGlass supports client-side division between quantitative datasets. This makes it possible
to quickly compare two datasets by visualizing their ratio as computed on loaded tiles
rather than the entire dataset:

.. code-block:: python

    t1 = Track(**track_def)
    t2 = Track(**{ **track_def, "tileset_uuid": "QvdMEvccQuOxKTEjrVL3wA" })
    t3 = t1 / t2

They can also be created using a constructor:

.. code-block:: python

    from higlass.client import DividedTrack

    t3 = DividedTrack(t1, t2)

The full example is here:

.. code-block:: python

  from higlass.utils import hg_cmap

  track_def = {
      "track_type": 'heatmap',
      "position": 'center',
      "tileset_uuid": 'CQMd6V_cRw6iCI_-Unl3PQ',
      "server": "http://higlass.io/api/v1/",
      "height": 210,
      "options": {}
  }

  t1 = Track(**track_def)
  t2 = Track(**{ **track_def, "tileset_uuid": "QvdMEvccQuOxKTEjrVL3wA" })
  t3 = (t1 / t2).change_attributes(
      options={
          'colorRange': hg_cmap('coolwarm'),
          'valueScaleMin': 0.1,
          'valueScaleMax': 10,
      })
  domain = [7e7,8e7]

  v1 = View([t1], x=0, width=4, initialXDomain=domain)
  v2 = View([t3], x=4, width=4, initialXDomain=domain)
  v3 = View([t2], x=8, width=4, initialXDomain=domain)

  display, server, viewconf = higlass.display([v1, v2, v3])
  display

.. image:: img/divided-by-track.png


Saving the view
---------------

The currently visible HiGlass view can be downloaded to a file:

.. code-block:: python

  display.save_as_png('/tmp/my_view.png')

Not that this function can only be used within a Jupyter notebook
and works asynchronously so the saved screenshot will not nessarily
be complete immediately after the function finishes executing

Authorization
-------------

If loading tiles from a secured server, the ``auth_token`` parameter takes the
string that will be used as the Authorization header on all tile requests sent
out by HiGlass:

.. code-block:: python

  (d,s,v) = higlass.display(views, auth_token='JWT DEADBEEF')



Other Examples
--------------

The examples below demonstrate how to use the HiGlass Python API to view data
locally in a Jupyter notebook or a browser-based HiGlass instance.

For a more complete overview, you can find the demos from the talk at
`github.com/higlass/scipy19 <https://github.com/higlass/scipy19>`_.

Jupyter HiGlass Component
^^^^^^^^^^^^^^^^^^^^^^^^^

To instantiate a HiGlass component within a Jupyter notebook, we first need
to specify which data should be loaded. This can be accomplished with the
help of the ``higlass.client`` module:

.. code-block:: python

    from higlass.client import View, Track
    import higlass


    view1 = View([
        Track(track_type='top-axis', position='top'),
        Track(track_type='heatmap', position='center',
              tileset_uuid='CQMd6V_cRw6iCI_-Unl3PQ',
              server="http://higlass.io/api/v1/",
              height=250,
              options={ 'valueScaleMax': 0.5 }),
    ])


Remote bigWig Files
^^^^^^^^^^^^^^^^^^^

bigWig files can be loaded either from the local disk or from remote http
servers. The example below demonstrates how to load a remote bigWig file from
the UCSC genome browser's archives. Note that this is a network-heavy operation
that may take a long time to complete with a slow internet connection.

.. code-block:: python

    from higlass.client import View, Track
    import higlass.tilesets

    ts1 = higlass.tilesets.bigwig(
        'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/encodeDCC/'
        'wgEncodeSydhTfbs/wgEncodeSydhTfbsGm12878InputStdSig.bigWig')

    tr1 = Track('horizontal-bar', tileset=ts1)
    view1 = View([tr1])
    display, server, viewconf = higlass.display([view1])

    display


Serving local data
^^^^^^^^^^^^^^^^^^

To view local data, we need to define the tilesets and set up a temporary
server.

Cooler Files
""""""""""""

Creating the server:

.. code-block:: python

    from higlass.client import View, Track
    from higlass.tilesets import cooler
    import higlass

    ts1 = cooler('../data/Dixon2012-J1-NcoI-R1-filtered.100kb.multires.cool')
    tr1 = Track('heatmap', tileset=ts1)
    view1 = View([tr1])
    display, server, viewconf = higlass.display([view1])

    display


.. image:: img/jupyter-hic-heatmap.png


BigWig Files
""""""""""""

In this example, we'll set up a server containing both a chromosome labels
track and a bigwig track. Furthermore, the bigwig track will be ordered
according to the chromosome info in the specified file.

.. code-block:: python


    from higlass.client import View, Track
    from higlass.tilesets import bigwig, chromsizes
    import higlass.tilesets

    chromsizes_fp = '../data/chromSizes_hg19_reordered.tsv'
    bigwig_fp = '../data/wgEncodeCaltechRnaSeqHuvecR1x75dTh1014IlnaPlusSignalRep2.bigWig'

    with open(chromsizes_fp) as f:
        chromsizes_arr = []
        for line in f.readlines():
            chrom, size = line.split('\t')
            chromsizes_arr.append((chrom, int(size)))

    cs = chromsizes(chromsizes_fp)
    ts = bigwig(bigwig_fp, chromsizes=chromsizes_arr)

    tr0 = Track('top-axis')
    tr1 = Track('horizontal-bar', tileset=ts)
    tr2 = Track('horizontal-chromosome-labels', position='top', tileset=cs)

    view1 = View([tr0, tr1, tr2])
    display, server, viewconf = higlass.display([view1])

    display

The client view will be composed such that three tracks are visible. Two of them
are served from the local server.

.. image:: img/jupyter-bigwig.png


Serving custom data
^^^^^^^^^^^^^^^^^^^


To display data, we need to define a tileset. Tilesets define two functions:
``tileset_info``:

.. code-block:: python

    > from higlass.tilesets import bigwig
    > ts1 = bigwig('http://hgdownload.cse.ucsc.edu/goldenpath/hg19/encodeDCC/wgEncodeSydhTfbs/wgEncodeSydhTfbsGm12878InputStdSig.bigWig')
    > ts1.tileset_info()
    {
     'min_pos': [0],
     'max_pos': [4294967296],
     'max_width': 4294967296,
     'tile_size': 1024,
     'max_zoom': 22,
     'chromsizes': [['chr1', 249250621],
                    ['chr2', 243199373],
                    ...],
     'aggregation_modes': {'mean': {'name': 'Mean', 'value': 'mean'},
                           'min': {'name': 'Min', 'value': 'min'},
                           'max': {'name': 'Max', 'value': 'max'},
                           'std': {'name': 'Standard Deviation', 'value': 'std'}},
     'range_modes': {'minMax': {'name': 'Min-Max', 'value': 'minMax'},
                     'whisker': {'name': 'Whisker', 'value': 'whisker'}}
     }

and ``tiles``:

.. code-block:: python

    > ts1.tiles(['x.0.0'])
    [('x.0.0',
      {'min_value': 0.0,
       'max_value': 9.119079544037932,
       'dense': 'Rh25PwcCcz...',   # base64 string encoding the array of data
       'size': 1,
       'dtype': 'float32'})]

The tiles function will always take an array of tile ids of the form ``id.z.x[.y][.transform]``
where ``z`` is the zoom level, ``x`` is the tile's x position, ``y`` is the tile's
y position (for 2D tilesets) and ``transform`` is some transform to be applied to the
data (e.g. normalization types like ``ice``).

Numpy Matrix
""""""""""""

By way of example, let's explore a numpy matrix by implementing the `tileset_info` and `tiles`
functions described above. To start let's make the matrix using the
`Eggholder function <https://en.wikipedia.org/wiki/Test_functions_for_optimization>`_.

.. code-block:: python

    import numpy as np

    dim = 2000
    I, J = np.indices((dim, dim))
    data = (
        -(J + 47) * np.sin(np.sqrt(np.abs(I / 2 + (J + 47))))
        - I * np.sin(np.sqrt(np.abs(I - (J + 47))))
    )

Then we can define the data and tell the server how to render it.

.. code-block:: python

    from  clodius.tiles import npmatrix
    from higlass.tilesets import Tileset

    ts = Tileset(
        tileset_info=lambda: npmatrix.tileset_info(data),
        tiles=lambda tids: npmatrix.tiles_wrapper(data, tids)
    )

    display, server, viewconf = higlass.display([
        View([
            Track(track_type='top-axis', position='top'),
            Track(track_type='left-axis', position='left'),
            Track(track_type='heatmap',
                  position='center',
                  tileset=ts,
                  height=250,
                  options={ 'valueScaleMax': 0.5 }),

        ])
    ])
    display

.. image:: img/eggholder-function.png

Displaying Many Points
""""""""""""""""""""""

To display, for example, a list of 1 million points in a HiGlass window inside of a Jupyter notebook.
First we need to import the custom track type for displaying labelled points:

.. code-block:: javascript

    %%javascript

    require(["https://unpkg.com/higlass-labelled-points-track@0.1.11/dist/higlass-labelled-points-track"],
        function(hglib) {

    });

Then we have to set up a data server to output the data in "tiles".

.. code-block:: python

    import numpy as np
    import pandas as pd
    from higlass.client import View, Track
    from higlass.tilesets import dfpoints

    length = int(1e6)
    df = pd.DataFrame({
        'x': np.random.random((length,)),
        'y': np.random.random((length,)),
        'v': range(1, length+1),
    })

    ts = dfpoints(df, x_col='x', y_col='y')

    display, server, viewconf = higlass.display([
        View([
            Track('left-axis'),
            Track('top-axis'),
            Track('labelled-points-track',
                   tileset=ts,
                   position='center',
                   height=600,
                   options={
                        'xField': 'x',
                        'yField': 'y',
                        'labelField': 'v'
            }),
        ])
    ])

    display

.. image:: img/jupyter-labelled-points.png

This same technique can be used to display points in a GeoJSON file.
First we have to extract the values from the GeoJSON file and
create a dataframe:

.. code-block:: python

    import math

    def lat2y(a):
      return 180.0/math.pi*math.log(math.tan(math.pi/4.0+a*(math.pi/180.0)/2.0))

    x = [t['geometry']['coordinates'][0] for t in trees['features']]
    y = [-lat2y(t['geometry']['coordinates'][1]) for t in trees['features']]
    names = [t['properties']['SPECIES'] for t in trees['features']]

    df = pd.DataFrame({ 'x': x, 'y': y, 'names': names })
    df = df.sample(frac=1).reset_index(drop=True)

And then create the tileset and track, as before.

.. code-block:: python

    from higlass.client import View, Track
    from higlass.tilesets import dfpoints

    ts = dfpoints(df, x_col='x', y_col='y')

    display, server, viewconf = higlass.display([
        View([
            Track('left-axis'),
            Track('top-axis'),
            Track('osm-tiles', position='center'),
            Track('labelled-points-track',
                   tileset=ts,
                   position='center',
                   height=600,
                   options={
                        'xField': 'x',
                        'yField': 'y',
                        'labelField': 'names'
            }),
        ])
    ])

    display

.. image:: img/geojson-jupyter.png


Other constructs
""""""""""""""""

The examples containing dense data above use the `bundled_tiles_wrapper_2d`
function to translate lists of tile_ids to tile data. This consolidates tiles
that are within rectangular blocks and fulfills them simultaneously. The
return type is a list of ``(tile_id, formatted_tile_data)`` tuples.

In cases where we don't have such a function handy, there's the simpler
`tiles_wrapper_2d` which expects the target to fullfill just single tile
requests:

.. code-block:: python

    from clodius.tiles.format import format_dense_tile
    from clodius.tiles.utils import tiles_wrapper_2d
    from higlass.tilesets import Tileset

    ts = Tileset(
        tileset_info=tileset_info,
        tiles=lambda tile_ids: tiles_wrapper_2d(tile_ids,
                        lambda z,x,y: format_dense_tile(tile_data(z, x, y)))
    )


In this case, we expect *tile_data* to simply return a matrix of values.


Troubleshooting
---------------

Accessing the server log
^^^^^^^^^^^^^^^^^^^^^^^^

A local server writes its log records to an in-memory `StringIO <https://docs.python.org/3/library/io.html#io.StringIO>`_ buffer. The server's name can be used to access its logger.

.. code-block:: python

    import logging

    logger = logging.getLogger(server.name)
    logger.info('Hi!')

    # convert the stream into a string
    print(server.log.getvalue())

    # write the log to a file
    with open('higlass-server.log', 'wt') as f:
        f.write(server.log.getvalue())

