from src import utils


def test_message_serialize():
    assert utils.message_serialize(
        "guilherme", "sair()", "ola") == b'27\x00guilherme\x00sair()\x00ola'
