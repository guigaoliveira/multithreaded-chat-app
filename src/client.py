from threading import Thread
import re
import socket
import utils


class Send:
    def __init__(self):
        self.__msg = ''
        self.new = True
        self.con = None

    def put(self, msg):
        self.__msg = msg
        if self.con != None:
            self.con.send(self.__msg)

    def get(self):
        return self.__msg

    def loop(self):
        return self.new


def esperar(tcp, send, host='localhost', port=9001):
    destino = (host, port)
    tcp.connect(destino)
    print(f"Conectado a {host}:{port}.")
    send.con = tcp
    while True:
        try:
            msg = tcp.recv(1024)
            if not msg:
                break
            msgDict = utils.message_parser(msg)
            if msgDict is not None:
                print(msgDict.get("data", ""))
        except socket.error:
            print("O cliente foi desconectado do servidor =/")
            break


if __name__ == '__main__':
    # cria um socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send = Send()
    # cria um Thread e usa a função esperar com dois argumentos
    processo = Thread(target=esperar, args=(sock, send))
    processo.start()

    msg = input()
    while True:
        if(msg == "sair()"):
            send.put(utils.message_serialize('>', 'sair', ''))
            break
        if(msg == "lista()"):
            send.put(utils.message_serialize('>', 'lista', ''))
        else:
            PRIVATE_CHAT_REGEX = r"^privado\((.{1,15})\)\s(.*)$"
            match = re.search(PRIVATE_CHAT_REGEX, msg, re.IGNORECASE)
            if match:
                nickname = match.group(1)
                data = match.group(2)
                send.put(utils.message_serialize(nickname, 'privado', data))
            else:
                send.put(utils.message_serialize('*', '-', msg))
        msg = input()

    processo.join()
    sock.close()
    exit()
