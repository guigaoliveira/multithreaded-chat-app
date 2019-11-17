import sys


def utf8len(s):
    return len(s.encode('utf-8'))


def message_serialize(nickname, command, data=''):
    HEADER_LENGTH = 24
    return b"".join([
        (f"{(len(data) + HEADER_LENGTH)}").encode(),
        (nickname.ljust(15, '&') + "\0").encode(),
        (command.ljust(7, '&') + "\0").encode(),
        data.encode()
    ])


def validate_data(messageDataList):

    if len(messageDataList) != 4:
        return False

    msgLength, nickname, command, _ = messageDataList
    MSG_MAX_LENGTH = 2  # o header já é maior que 2 bytes
    NICKNAME_MAX_LENGTH = 15
    COMMAND_MAX_LENGTH = 7
    return utf8len(msgLength) <= MSG_MAX_LENGTH \
        and utf8len(nickname) <= NICKNAME_MAX_LENGTH \
        and utf8len(command) <= COMMAND_MAX_LENGTH


def message_parser(message):

    if not message or message is None:
        return None

    message_in_utf8 = message.decode("utf-8")
    messageDataList = [message_in_utf8[0:2]] + message_in_utf8[2:].split("\0")

    if not validate_data(messageDataList):
        return None

    msgLength, nickname, command, data = messageDataList
    return {
        "msgLength": msgLength,
        "nickname": nickname.rstrip('&'),
        "command": command.rstrip('&'),
        "data": data
    }


def on_forced_exit(connection, stop_event):
    def signal_handler(sig, frame):
        stop_event.set()
        connection.close()
        sys.exit(0)

    return signal_handler
