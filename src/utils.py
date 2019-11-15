import sys


def utf8len(s):
    return len(s.encode('utf-8'))


def message_serialize(username, command, data):
    HEADER_LENGTH = 24
    return b"".join([
        (f"{(len(data) + HEADER_LENGTH)}").encode(),
        (username + "\0").encode(),
        (command + "\0").encode(),
        data.encode()
    ])


def validate_data(messageDataList):
    if len(messageDataList) != 4:
        return False
    msgLength, username, command, _ = messageDataList
    MSG_MAX_LENGTH = 2  # o header já é maior que 2 bytes
    username_MAX_LENGTH = 15
    COMMAND_MAX_LENGTH = 7
    return utf8len(msgLength) <= MSG_MAX_LENGTH \
        and utf8len(username) <= username_MAX_LENGTH \
        and utf8len(command) <= COMMAND_MAX_LENGTH


def message_parser(message):
    msg_utf8 = message.decode("utf-8")
    messageDataList = [msg_utf8[0:2]] + msg_utf8[2:].split("\0")
    if validate_data(messageDataList):
        msgLength, username, command, data = messageDataList
        return {
            "msgLength": msgLength,
            "username": username,
            "command": command,
            "data": data
        }
    return None
