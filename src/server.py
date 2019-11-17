import socket
from threading import Thread, Event
import re
import utils
import sys


class ClientDisconnection(Exception):
    pass


def create_socket(HOST='', PORT=9001):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    sock.settimeout(0.1)
    return sock


def read_socket_data(connection):
    try:
        BUFFER_SIZE = 1024
        data = connection.recv(BUFFER_SIZE)
        return data
    except:
        return None


def get_key_by_value(dict, value):
    names = list(dict.values())
    if(value in names):
        return list(dict.keys())[names.index(value)]
    return None


def get_client_list(clients):
    result = ""
    for connection, name in clients.copy().items():
        try:
            host, port = connection.getpeername()
            result += f"<{name}, {host}, {port}>\n"
        except:
            del clients[connection]
    return result[:-1]


def broadcast_chat_message(clients, msg, nickname=""):
    msg_to_send = f"[SALA] {nickname} escreveu: {msg}"
    print(msg_to_send)
    for connection in clients.copy():
        try:
            connection.send(utils.message_serialize("*", "", msg_to_send))
        except:
            del clients[connection]


def handle_client_exit_command(connection, clients, nickname_client):
    print(f"O usuário *{nickname_client}* saiu do chat.")
    connection.close()
    broadcast_chat_message(clients, f"{nickname_client} saiu!", "O servidor")


def handle_private_message(connection, nickname_client, nickname_recipient, msg):
    try:
        recipient_connection = get_key_by_value(clients, nickname_recipient)
        if recipient_connection:
            recipient_connection.send(utils.message_serialize(
                nickname_recipient, "privado", f"[PRIVADO] {nickname_client} escreveu: {msg}"))
        else:
            connection.send(utils.message_serialize(
                nickname_client, "-", f"O usuário {nickname_recipient} não existe."))
    except:
        return


def get_nickname_client(connection):
    # provavelmente cada user deve ser único
    is_valid_user = False
    nickname_client = None
    while not is_valid_user:
        try:
            connection.send(utils.message_serialize(
                "-", "-", "Digite um nickname válido:"))

            nameInfo = utils.message_parser(read_socket_data(connection))

            if nameInfo is None:
                break

            nickname_client = nameInfo.get("data", "")
            is_valid_user = not nickname_client in clients.values()

            if(is_valid_user):
                return nickname_client

            connection.send(utils.message_serialize(
                "-", "-", "Um usuário com esse nickname já existe."))
        except:
            return None


def send_welcome_msg_to_new_user(connection, nickname_client):
    msg_welcome = f"Seja bem vindo {nickname_client}!\n" + \
        "Para listar usuários, digite lista(); \n" + \
        "Para sair do chat, digite sair();"
    connection.send(utils.message_serialize(nickname_client, "", msg_welcome))
    return nickname_client


def notify_other_users_about_new_user(clients, nickname_client):
    msg_notification = f"O usuário *{nickname_client}* entrou na sala."
    print(msg_notification)
    broadcast_chat_message(
        clients, f"o usuário *{nickname_client}* entrou...", "O servidor")


def perform_action_by_command(connection, clients, nickname_client, msg_info):
    try:
        command = msg_info.get("command", "")
        nickname_recipient = msg_info.get("nickname", "")
        payload = msg_info.get("data", "")

        if nickname_recipient == "*" and command == "-":
            broadcast_chat_message(clients, payload, nickname_client)
        elif nickname_recipient == ">" and command == "sair":
            raise ClientDisconnection("Cliente executou comando de saída")
        elif nickname_recipient == ">" and command == "lista":
            connection.send(utils.message_serialize(
                nickname_client, "lista", get_client_list(clients)))
        elif (nickname_recipient != "*" or nickname_recipient == ">") and command == "privado":
            handle_private_message(
                connection, nickname_client, nickname_recipient, payload)
        else:
            print(
                f"O cliente *{nickname_client}* enviou um comando não reconhecido.")
    except:
        handle_client_exit_command(
            connection, clients, nickname_client)


def get_client_messages(connection, address, clients, stop_event):
    try:
        nickname_client = get_nickname_client(connection)
        if nickname_client is None:
            print("%s:%s está desconectado." % address)
            return
        clients[connection] = nickname_client

        send_welcome_msg_to_new_user(connection, nickname_client)
        notify_other_users_about_new_user(clients, nickname_client)

        while not stop_event.is_set():
            msg_info = utils.message_parser(read_socket_data(connection))

            if msg_info is None:
                raise ClientDisconnection('O cliente está desconectado.')

            perform_action_by_command(
                connection, clients, nickname_client, msg_info)
    except:
        handle_client_exit_command(
            connection, clients, nickname_client)


def get_new_connection(sock, clients, stop_event):
    while not stop_event.is_set():
        try:
            connection, address = sock.accept()
            print("%s:%s está conectado." % address)
            get_messages_thread = Thread(target=get_client_messages, args=(
                connection, address, clients, stop_event, ))
            get_messages_thread.start()
        except socket.timeout:
            pass
        except:
            stop_event.set()
            break


def run_server_exit_command(sock, clients):
    for connection in clients:
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
    clients.clear()
    stop_event.set()
    sock.close()


def get_and_run_server_commands(sock, clients):
    keyboard_input = input()
    while True:
        if(keyboard_input == "lista()"):
            print(get_client_list(clients))
        elif(keyboard_input == "sair()"):
            run_server_exit_command(sock, clients)
            break
        else:
            print("Comando não reconhecido pelo servidor.")
        keyboard_input = input()


def on_forced_exit():
    stop_event.set()
    sock.close()
    sys.exit(0)


if __name__ == "__main__":
    sock = create_socket()
    print("Esperando por uma conexão...")
    clients = {}
    try:
        stop_event = Event()
        connections_thread = Thread(target=get_new_connection, args=(
            sock, clients, stop_event, ))
        connections_thread.start()
        get_and_run_server_commands(sock, clients)
        connections_thread.join()
        on_forced_exit()
    except:
        on_forced_exit()
