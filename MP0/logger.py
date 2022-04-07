from socket import *
from threading import Thread
import sys, time


def main():
    if len(sys.argv) != 2:
        Exception("The number of input parameters should be 2")
        return
    port = int(sys.argv[1])
    with socket(AF_INET, SOCK_STREAM) as s:
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", port))
        s.listen(SOMAXCONN)
        while True:
            client_socket, clientAddr = s.accept()
            new_event = Thread(target=log, args=(client_socket,))
            new_event.start()


def log(s):
    while True:
        recv_data = s.recv(1024).decode("utf-8")
        if len(recv_data) != 0:
            print(recv_data, " ")
        else:
            return


if __name__ == '__main__':
    main()

