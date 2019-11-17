from threading import Thread, Event
import re
import socket
import utils
import sys


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


def handle_disconnection(stop_event):
    stop_event.set()
    print("Cliente está desconectado do servidor.")


def get_messages(connection, stop_event):
    while not stop_event.is_set():
        try:
            msg = connection.recv(1024)
            if not msg:
                handle_disconnection(stop_event)
                break
            msg_info = utils.message_parser(msg)
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
                connection.send(utils.message_serialize('>', 'sair', ''))
                handle_disconnection(stop_event)
                break
            elif(keyboard_input == "lista()"):
                connection.send(utils.message_serialize('>', 'lista', ''))
            else:
                PRIVATE_CHAT_REGEX = r"^privado\((.{1,16})\)\s(.*)$"
                match = re.search(PRIVATE_CHAT_REGEX,
                                  keyboard_input, re.IGNORECASE)
                if match:
                    nickname = match.group(1)
                    data = match.group(2)
                    connection.send(utils.message_serialize(
                        nickname, 'privado', data))
                else:
                    connection.send(utils.message_serialize(
                        '*', '-', keyboard_input))
            keyboard_input = input()
    except:
        handle_disconnection(stop_event)


if __name__ == '__main__':
    connection = create_connection(socket)
    if connection is not None:
        try:
            stop_event = Event()
            thread_connections = Thread(
                target=get_messages, args=(connection, stop_event, ))
            Thread(
                target=send_messages, args=(connection, stop_event, ), daemon=True).start()
            thread_connections.start()
            thread_connections.join()
        except:
            stop_event.set()
            connection.close()
            sys.exit(0)
