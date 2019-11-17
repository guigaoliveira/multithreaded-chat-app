from threading import Thread, Event
import re
import socket
import util
import sys
import signal


def create_connection(socket, HOST='', PORT=9001):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        sock.connect((HOST, PORT))
        print(f"Conectado a {HOST}:{PORT}.")
        return sock
    except socket.error:
        print("Não foi possível conectar ao servidor {HOST}:{PORT}.")
        return None


def handle_disconnection(connection, stop_event):
    util.on_forced_exit(connection, stop_event)
    print("O cliente está desconectado do servidor.")


def get_messages(connection, stop_event):
    while not stop_event.is_set():
        try:
            msg = connection.recv(1024)
            if not msg:
                break
            msg_info = util.message_parser(msg)
            if msg_info is not None:
                print(msg_info.get("data", ""))
        except socket.timeout:
            pass
        except:
            break


def send_messages(connection, stop_event):
    keyboard_input = input()
    try:
        while not stop_event.is_set():
            if(keyboard_input == "sair()"):
                connection.send(util.message_serialize('>', 'sair', ''))
                handle_disconnection(connection, stop_event)
                break
            elif(keyboard_input == "lista()"):
                connection.send(util.message_serialize('>', 'lista', ''))
            else:
                PRIVATE_CHAT_REGEX = r"^privado\((.{1,16})\)\s(.*)$"
                groups_values = re.findall(PRIVATE_CHAT_REGEX, keyboard_input)
                if len(groups_values):
                    nickname, data = groups_values[0]
                    connection.send(util.message_serialize(
                        nickname, 'privado', data))
                else:
                    connection.send(util.message_serialize(
                        '*', '-', keyboard_input))
            keyboard_input = input()
    except:
        handle_disconnection(connection, stop_event)


if __name__ == '__main__':
    connection = create_connection(socket)
    stop_event = Event()
    signal.signal(signal.SIGTSTP,
                  util.on_forced_exit(connection, stop_event))
    signal.signal(signal.SIGINT,
                  util.on_forced_exit(connection, stop_event))
    if connection is not None:
        try:
            thread_connections = Thread(
                target=get_messages, args=(connection, stop_event, ))
            Thread(
                target=send_messages, args=(connection, stop_event, ), daemon=True).start()
            thread_connections.start()
            thread_connections.join()
        except:
            util.on_forced_exit(connection, stop_event)
