import higlass.client as hgc
import json

def test_viewconf_createion():
    conf = hgc.ViewConf()
    view = conf.add_view()

    track = view.add_track(track_type='heatmap',
            server='http://localhost:{}/api/v1/'.format(8000),
            tileset_uuid='xx', position='top', 
            height=200)

    conf = json.loads(json.dumps(conf.to_dict()))
