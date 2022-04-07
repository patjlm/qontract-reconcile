from version import version


def test_version():
    assert version("0.4.0") == "0.4.0"
    assert version("0.4.0-6-gaaaaaaa") == "0.4.1-6.aaaaaaa"
