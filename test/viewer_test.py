from unittest.mock import patch

from higlass.client import View, Track
from higlass.viewer import display


def test_create_display():
    """Test to make sure we can create a display."""
    with patch("higlass.server.Server") as _:
        (_, _, viewconf) = display([View([Track("top-axis")])])

        vc_dict = viewconf.to_dict()

        assert len(vc_dict["views"]) == 1

        (_, _, viewconf) = display([[Track("top-axis")]])

        vc_dict = viewconf.to_dict()

        assert len(vc_dict["views"]) == 1
