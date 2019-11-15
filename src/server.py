import socket
from threading import Thread
import re
import utils


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


def broadcast(msg, username=""):
    for connection in clients:
        connection.send(utils.message_serialize(
            "*", "", f"[SALA] {username} escreveu: {msg}"))


def handle_exit_request(connection, clients):
    connection.close()
    name = clients[connection]
    del clients[connection]
    broadcast(f"{name} saiu!")


def handle_private_message(connection, client_name, recipient_username, msg):
    recipient_connection = getKeyByValue(clients, recipient_username)

    if recipient_connection:
        recipient_connection.send(utils.message_serialize(
            recipient_username, "privado", f"[PRIVADO] {client_name} escreveu: {msg}"))
    else:
        connection.send(utils.message_serialize(
            client_name, "-", f"O usuário {recipient_username} não existe."))


def get_username(connection, buffer_size):
    # provavelmente cada user deve ser único
    connection.send(utils.message_serialize(
        "-", "-", "Digite seu nome de usúario."))
    nameInfo = utils.message_parser(connection.recv(buffer_size))

    if nameInfo is None:
        return

    client_username = nameInfo.get("data", "")

    return client_username


def handle_messages(connection, clients):
    BUFFER_SIZE = 1024
    client_username = get_username(connection, BUFFER_SIZE)
    welcome_msg = f"Seja bem vindo {client_username}! Para sair do chat, digite sair()."
    connection.send(utils.message_serialize(client_username, "", welcome_msg))

    broadcast(f"{client_username} entrou...", "O servidor")

    clients[connection] = client_username

    while True:
        try:
            packet = connection.recv(BUFFER_SIZE)

            if not packet:
                break

            packetInfo = utils.message_parser(packet)

            if packetInfo is None:
                continue

            command = packetInfo.get("command", "")
            recipient_username = packetInfo.get("username", "")
            payload = packetInfo.get("data", "")

            if recipient_username == "*" and command == "-":
                broadcast(payload, client_username)
            if recipient_username == ">" and command == "sair":
                handle_exit_request(connection, clients)
            if recipient_username == ">" and command == "lista":
                connection.send(utils.message_serialize(
                    client_username, "lista", get_client_list(clients)))
            if (recipient_username != "*" or recipient_username == ">") and command == "privado":
                handle_private_message(
                    connection, client_username, recipient_username, payload)
        except socket.error:
            break


def handle_connections(clients):
    while True:
        connection, address = sock.accept()
        print("%s:%s está conectado." % address)
        Thread(target=handle_messages, args=(connection, clients,)).start()


def handle_exit_command(clients):
    for connection in clients:
        connection.close()
    clients.clear()


if __name__ == "__main__":
    HOST = ''
    PORT = 9001

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print("Esperando por uma conexão...")
    connections_thread = Thread(target=handle_connections, args=(clients, ))
    connections_thread.start()
    keyboard_input = input()
    clients = {}
    while True:
        if(keyboard_input == "lista()"):
            print(get_client_list(clients))
        if(keyboard_input == "sair()"):
            handle_exit_command(clients)
        keyboard_input = input()

    connections_thread.join()
    sock.close()
