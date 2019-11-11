import sys


def utf8len(s):
    return len(s.encode('utf-8'))


def message_serialize(nickname, command, data):
    HEADER_LENGTH = 24
    return b"".join([
        (f"{(len(data) + HEADER_LENGTH)}" + "\0").encode(),
        (nickname + "\0").encode(),
        (command + "\0").encode(),
        data.encode()
    ])


def validate_data(messageDataList):
    msgLength, nickname, command, _ = messageDataList
    MSG_MAX_LENGTH = 15
    NICKNAME_MAX_LENGTH = 255
    COMMAND_MAX_LENGTH = 63
    return utf8len(msgLength) < MSG_MAX_LENGTH \
        and utf8len(nickname) < NICKNAME_MAX_LENGTH \
        and utf8len(command) < COMMAND_MAX_LENGTH


def message_parser(message):
    messageDataList = message.split("\0")
    if validate_data(messageDataList):
        msgLength, nickname, command, data = messageDataList
        return {
            "msgLength": msgLength,
            "nickname": nickname,
            "command": command,
            "data": data
        }
    return None
