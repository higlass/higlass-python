from higlass.client import Track, View, projection_adder
import higlass


def test_viewport_projection():
    view1 = View([Track("top-axis")])

    adder = projection_adder(view1)

    view2 = View([adder(Track("top-axis"))])

    (display, server, viewconf) = higlass.display([view1, view2])

    print(viewconf.to_dict()["views"][1]["tracks"]["top"][0])
    assert (
        "server"
        not in viewconf.to_dict()["views"][1]["tracks"]["top"][0]["contents"][1]
    )

    server.stop()
