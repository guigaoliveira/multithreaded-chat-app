import socket
from threading import Thread
import re
import utils

HOST = ''
PORT = 9001
BUFFER_SIZE = 1024
ADDR = (HOST, PORT)
clients = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(ADDR)


def bytesFormat(data):
    return bytes(data, "utf-8")


def getKeyByValue(dict, value):
    names = list(dict.values())
    if(value in names):
        return list(dict.keys())[names.index(value)]
    return None


def get_client_list(clients):
    result = ""
    for connection, name in clients.items():
        host, port = connection.getpeername()
        result += f"<{name}, {host}, {port}>\n"
    return result[:-1]


def broadcast(msg, prefix=""):
    for connection in clients:
        connection.send(utils.message_serialize(
            "*", "", f"{prefix} escreveu: {msg}"))


def handle_exit_request(connection):
    connection.close()
    name = clients[connection]
    del clients[connection]
    broadcast(bytesFormat(f"{name} saiu!"))


def handle_private_message(connection, client_name, nickname, data):
    recipient_connection = getKeyByValue(clients, nickname)
    if recipient_connection:
        recipient_connection.send(utils.message_serialize(
            nickname, "privado", data))
    else:
        connection.send(utils.message_serialize(
            client_name, "-", f"O usuário {nickname} não existe."))


def handle_connections():
    while True:
        connection, address = sock.accept()
        print("%s:%s está conectado." % address)
        Thread(target=handle_messages, args=(connection,)).start()


def handle_messages(connection):
    # provavelmente cada user deve ser único
    connection.send(utils.message_serialize(
        "-", "-", "Digite seu nome de usúario."))
    nameInfo = utils.message_parser(
        connection.recv(BUFFER_SIZE))

    if nameInfo is None:
        return

    client_nickname = nameInfo.get("data", "")

    connection.send(
        utils.message_serialize(client_nickname, "",
                                f"Seja bem vindo {client_nickname}! \
                                Para sair do chat, digite sair()."))

    broadcast(f"{client_nickname} entrou...", "O Servidor")

    clients[connection] = client_nickname

    while True:
        msgInfo = utils.message_parser(connection.recv(BUFFER_SIZE))

        if msgInfo is None:
            continue

        msg_command = msgInfo.get("command", "")
        msg_nickname = msgInfo.get("nickname", "")
        msg_data = msgInfo.get("data", "")

        if msg_nickname == "*":
            broadcast(msg_data, client_nickname)
        if msg_nickname == ">" and msg_command == "sair":
            handle_exit_request(connection)
        if msg_nickname == ">" and msg_command == "lista":
            connection.send(bytesFormat(get_client_list(clients)))
        if (msg_nickname != "*" or msg_nickname == ">") and msg_command == "privado":
            handle_private_message(
                connection, client_nickname, msg_nickname, msg_data)


if __name__ == "__main__":
    sock.listen(5)
    print("Esperando por uma conexão...")
    connections_thread = Thread(target=handle_connections)
    connections_thread.start()

    msg = input()
    while True:
        if(msg == "lista()"):
            print(get_client_list(clients))
        """ if(msg == "sair()"):
            for connection in clients:
                connection.close() """
        msg = input()

    connections_thread.join()
    sock.close()
