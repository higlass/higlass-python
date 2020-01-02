from higlass.client import Track, View, ViewConf
import json


def test_viewconf_creation():
    conf = ViewConf()

    view = conf.create_view()

    track = view.create_track(
        "heatmap",
        server="http://localhost:{}/api/v1/".format(8000),
        tileset_uuid="xx",
        height=200,
        position="top",
    )

    conf1_dict = conf.to_dict()
    conf2 = ViewConf.from_dict(conf1_dict)
    assert conf2.to_dict() == conf1_dict
