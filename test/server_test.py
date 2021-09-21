from unittest.mock import Mock, patch

import higlass.server as server


def test_tcp():
    s = server.Server([], host="localhost", port=1234)
    with patch("requests.head") as head, patch("multiprocess.Process") as mp:
        head.ok = True
        s.start()

    expected_api_address = "http://localhost:1234/api/v1"
    assert s.api_address == expected_api_address


def test_tcp_root_api_address():
    s = server.Server(
        [], host="localhost", port=1234, root_api_address="http://{host}:{port}/test"
    )
    with patch("requests.head") as head, patch("multiprocess.Process") as mp:
        head.ok = True
        s.start()

    expected_api_address = "http://localhost:1234/test/api/v1"
    assert s.api_address == expected_api_address


def test_unix_host_file():
    filename = "/tmp/s.sock"
    s = server.Server([], host=f"unix://{filename}")
    with patch("requests.head") as head, patch("multiprocess.Process") as mp:
        head.ok = True
        s.start()

    expected_api_address = "http+unix://" + filename.replace("/", "%2F") + "/api/v1"
    assert s.api_address == expected_api_address


def test_unix_host_dir_with_port():
    filename = "/tmp/s.sock"
    s = server.Server([], host=f"unix:///tmp", port="s.sock")
    with patch("requests.head") as head, patch("multiprocess.Process") as mp, patch(
        "os.makedirs"
    ) as _:
        head.ok = True
        s.start()

    expected_api_address = "http+unix://" + filename.replace("/", "%2F") + "/api/v1"
    assert s.api_address == expected_api_address


def test_unix_host_dir_without_port():
    filename = "/tmp/0"
    s = server.Server([], host=f"unix:///tmp", port=None)
    with patch("requests.head") as head, patch(
        "higlass.server.get_free_socket", return_value=0
    ) as _, patch("multiprocess.Process") as mp, patch("os.makedirs") as _:
        head.ok = True
        s.start()

    expected_api_address = "http+unix://" + filename.replace("/", "%2F") + "/api/v1"
    assert s.api_address == expected_api_address


def test_unix_root_api_address():
    filename = "/tmp/s.sock"
    s = server.Server(
        [],
        host=f"unix://{filename}",
        root_api_address="http+unix://{unix_filename}/test",
    )
    with patch("requests.head") as head, patch("multiprocess.Process") as mp:
        head.ok = True
        s.start()

    expected_api_address = f"http+unix://{filename}/test/api/v1"
    assert s.api_address == expected_api_address
