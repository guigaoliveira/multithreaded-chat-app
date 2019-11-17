from src import util


def test_message_parser():
    assert util.message_parser(
        b"50-&&&&&&&&&&&&&&\x00-&&&&&&\x00Digite um nickname v\xc3\xa1lido:") \
        == {'msgLength': '50', 'nickname':
            '-',
            'command': '-',
            'data': 'Digite um nickname válido:'
            }
