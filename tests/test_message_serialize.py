from src import util


def test_message_serialize():
    assert util.message_serialize(
        "guilherme", "sair", "ola") == b'27guilherme&&&&&&\x00sair&&&\x00ola'
