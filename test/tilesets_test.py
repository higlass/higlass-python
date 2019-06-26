import higlass.tilesets as hgti

import pandas as pd

def test_dfpoints():
    df = pd.DataFrame({
        'a': [1.0, 2.0, 3.0],
        'b': [5.0, 6.0, 7.0],
        'x': ['hi', 'there', 'you']
    })

    ts = hgti.dfpoints(
        df, 'a', 'b', 'x'
    )

    tsinfo = ts.tileset_info()

    assert len(tsinfo['min_pos']) == 2
    assert 'max_width' in tsinfo
