Python API
##########

The HiGlass python API provides a functionality for starting a
lightweight server, creating viewconfs and displaying a HiGlass
component within Jupyter.

higlass
*******

.. automethod:: higlass.viewer.display

higlass.server
**************

.. autoclass:: higlass.server.Server
    :members: __init__, start

higlass.client
**************

.. autoclass:: higlass.client.View
    :members: __init__

.. autoclass:: higlass.client.Track
    :members: __init__
