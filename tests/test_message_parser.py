from src import util


def test_message_parser():
    assert util.message_parser(
        "3\x00guilherme\x00sair()\x00ola") == {'msgLength': '3', 'nickname':
                                               'guilherme',
                                               'command': 'sair()',
                                               'data': 'ola'
                                               }
