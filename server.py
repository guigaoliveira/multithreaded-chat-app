import socket
from threading import Thread
import re

def int_to_bytes(val, num_bytes):
    return [(val & (0xff << pos*8)) >> pos*8 for pos in range(num_bytes)]

def bytesFormat(data):
    return bytes(data, "utf-8")


def getKeyByValue(dict, value):
    return list(dict.keys())[list(dict.values()).index(value)]


def get_client_list(clients):
    result = ""
    for client, name in clients.items():
        host, port = client.getpeername()
        result += f"<{name}, {host}, {port}>\n"
    return result[:-1]


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""
    for sock in clients:
        sock.send(bytesFormat(prefix) + msg)


def handle_exit_request(client):
    client.close()
    name = clients[client]
    del clients[client]
    broadcast(bytesFormat(f"{name} saiu!"))


def handle_private_message(msg):
    match = re.search(r"privado\((\w+)\)", msg, re.IGNORECASE)
    if match:
        client_name = match.group(1)
        return getKeyByValue(clients, client_name)
    return None


def handle_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s está conectado." % client_address)
        client.send(bytesFormat("Digite seu nickname."))
        Thread(target=handle_messages, args=(client,)).start()


def handle_messages(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    client.send(bytesFormat(
        f"Seja bem vindo {name}! Para sair do chat, digite sair()."))
    broadcast(bytesFormat(f"{name} entrou..."))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        msgStr = msg.decode("utf-8")
        print(msg)
        if msgStr != "sair()":
            if msgStr == "lista()":
                client.send(bytesFormat(get_client_list(clients)))
                break
            private_client = handle_private_message(msgStr)
            if private_client:
                private_client.send(bytesFormat("te mandaram um privado lek"))
                break
            broadcast(msg, name+": ")
        else:
            handle_exit_request(client)
            break


clients = {}

HOST = ''
PORT = 9001
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    print(int_to_bytes(5, 2))
    ACCEPT_THREAD = Thread(target=handle_connections)
    ACCEPT_THREAD.start()

    msg = input()
    while True:
        if(msg == "lista()"):
            print(get_client_list(clients))
        msg = input()

    ACCEPT_THREAD.join()
    SERVER.close()
