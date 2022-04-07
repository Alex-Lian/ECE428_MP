from socket import *
import os, sys, time


def main():
    if len(sys.argv) != 4:
        Exception("The number of input parameters should be 4")
        return
    node, ip = sys.argv[1:3]
    port = int(sys.argv[3])
    with socket(AF_INET, SOCK_STREAM) as s:
        address = (ip, port)
        s.connect(address)
        info = "{0} - {1} connected {2}".format(time.time(), node, "\n").encode("utf-8")
        s.send(info)
        for line in sys.stdin:
            timestamps, msg = line.split(' ')
            info = "{0} {1} {2}{3}".format(timestamps, node, "\n", msg).encode("utf-8")
            s.send(info)
        info = "{0} - {1} disconnected".format(time.time(), node).encode("utf-8")
        s.send(info)
        s.close()


if __name__ == '__main__':
    main()
