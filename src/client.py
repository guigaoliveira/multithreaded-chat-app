from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import re
import utils

PRIVATE_CHAT_REGEX = r"^privado\((.{1,15})\)\s(.*)$"


class Send:
    def __init__(self):
        self.__msg = ''
        self.new = True
        self.con = None

    def put(self, msg):
        self.__msg = msg
        if self.con != None:
            # envia um mensagem atravez de uma conexão socket
            self.con.send(self.__msg)

    def get(self):
        return self.__msg

    def loop(self):
        return self.new

# função esperar - Thread


def esperar(tcp, send, host='localhost', port=9001):
    destino = (host, port)
    tcp.connect(destino)

    while True:
        print(f"Conectado a {host}:{port}.")
        send.con = tcp
        while True:
            # aceita uma mensagem
            msg = tcp.recv(1024)
            if not msg:
                break
            msgDict = utils.message_parser(msg)
            if msgDict is not None:
                print(msgDict.get("data", ""))


if __name__ == '__main__':
    # cria um socket
    tcp = socket(AF_INET, SOCK_STREAM)
    send = Send()
    # cria um Thread e usa a função esperar com dois argumentos
    processo = Thread(target=esperar, args=(tcp, send))
    processo.start()

    msg = input()
    while True:
        if(msg == "sair()"):
            send.put(utils.message_serialize('>', 'sair', ''))
        if(msg == "lista()"):
            send.put(utils.message_serialize('>', 'lista', ''))
        match = re.search(PRIVATE_CHAT_REGEX, msg, re.IGNORECASE)
        if match:
            nickname = match.group(1)
            data = match.group(2)
            send.put(utils.message_serialize(nickname, 'privado', data))
        else:
            send.put(utils.message_serialize('*', '-', msg))
        msg = input()

    processo.join()
    tcp.close()
    exit()
