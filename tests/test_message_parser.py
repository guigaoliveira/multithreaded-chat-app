from src import utils


def test_message_parser():
    assert protocol.message_parser(
        "3\x00guilherme\x00sair()\x00ola") == {'msgLength': '3', 'nickname':
                                               'guilherme',
                                               'command': 'sair()',
                                               'data': 'ola'
                                               }
