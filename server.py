import socket
from threading import Thread


def bytesFormat(data):
    return bytes(data, "utf-8")


def handle_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytesFormat(
            "Greetings from the cave! Now type your name and press enter!"))
        addresses[client] = client_address
        Thread(target=handle_messages, args=(client,)).start()


def handle_messages(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytesFormat(welcome))
    msg = "%s has joined the chat!" % name
    broadcast(bytesFormat(msg))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        print(msg)
        if msg != bytesFormat("{quit}"):
            broadcast(msg, name+": ")
        else:
            client.send(bytesFormat("{quit}"))
            client.close()
            del clients[client]
            broadcast(bytesFormat(f"{name} has left the chat."))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytesFormat(prefix) + msg)


clients = {}
addresses = {}

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
    ACCEPT_THREAD = Thread(target=handle_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
