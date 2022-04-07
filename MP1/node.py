import sys
import time
from collections import defaultdict
from socket import *
from threading import Thread, Lock

total_num = 0
connect_number = 0
connect_number_lock = Lock()
node_socket_mapping = dict()
node_socket_mapping_lock = Lock()
timestamp = 0
timestamp_lock = Lock()
cur_node_name = ""
balance = defaultdict(int)


class Message:
    def __init__(self, content="", initial_ts=0, initial_node="", cur_ts=0, cur_node="", status=0):
        self.content = content
        self.initial_ts = initial_ts
        self.initial_node = initial_node
        self.cur_ts = cur_ts
        self.cur_node = cur_node
        self.status = status

        self.label = (self.content, int(self.initial_ts), self.initial_node)

    def get_message_string(self):
        # convert the class to string message so that you can send via network
        return "@".join(
            [self.content, str(self.initial_ts), self.initial_node, str(self.cur_ts), self.cur_node, str(self.status)]) + "#"


class Queue:
    def __init__(self):
        self.entries = []
        self.length = 0

    def sort(self):
        self.entries = sorted(self.entries, key=lambda x: (x.cur_ts, int(x.cur_node.split("node")[-1])))

    def enqueue(self, item):
        self.entries.append(item)
        self.length = self.length + 1
        self.sort()

    def dequeue(self):
        self.length = self.length - 1
        dequeued = self.entries[0]
        self.entries = self.entries[1:]
        return dequeued

    def get_msg(self, input_label):
        for i in range(len(self.entries)):
            if self.entries[i].label == input_label:
                return self.entries[i]
        raise Exception("get msg failed")

    def update(self, update_msg):
        for i in range(len(self.entries)):
            if self.entries[i].label == update_msg.label:
                self.entries[i] = update_msg
                break
        self.sort()

    def peek(self):
        return self.entries[0]

    def get_status(self, input_label):
        # print("--entries--")
        # print(input_label)
        for i in range(len(self.entries)):
            # print("self.entries[i].label")
            # print(self.entries[i].label)
            if self.entries[i].label == input_label:
                return self.entries[i].status
        raise Exception("get status fail")

    def increase_status(self, input_label):
        for i in range(len(self.entries)):
            if self.entries[i].label == input_label:
                self.entries[i].status += 1

    def check_deliver(self):
        if self.length <= 0:
            return False
        if self.peek().status == -1:
            return True
        else:
            return False

    def delete_node(self, node_name):
        for i in range(len(self.entries)):
            if self.entries[i].initial_node == node_name:
                del self.entries[i]
                self.length -= 1


cur_queue = Queue()
cur_queue_lock = Lock()


def handle_failure(node_name):
    global cur_queue, total_num
    total_num -= 1
    cur_queue.delete_node(node_name)
    del node_socket_mapping[node_name]
    for i in range(cur_queue.length):
        if cur_queue.entries[i].status == total_num - 1:
            cur_queue.entries[i].status = -1
            multicast(cur_queue.entries[i].get_message_string())



def multicast(msg):
    global node_socket_mapping, total_num, cur_queue
    node_socket_mapping_lock.acquire()
    fail_node = []
    for key, value in node_socket_mapping.items():
        # send message, check if it has error
        try:
            # print("--send msg--")
            # print(msg)
            value.send(msg.encode("utf-8"))
        except:
            value.close()
            fail_node.append(key)
    for node in fail_node:
        node_socket_mapping_lock.release()
        handle_failure(node)
        node_socket_mapping_lock.acquire()
    node_socket_mapping_lock.release()


def show_bank():
    global balance
    cur_str = ""
    for i in sorted(balance):
        cur_str += (" " + str(i) + ":" + str(balance[i]))
    print("BALANCES", cur_str, '\n')


def deliver_queue_head():
    global cur_queue, balance
    # print("show cur_queue")
    # for i in cur_queue.entries:
    #     print(i.get_message_string())
    deliver_content = cur_queue.dequeue().content
    if "DEPOSIT" in deliver_content:
        _, user, num = deliver_content.split()
        balance[user] += int(num)
        show_bank()
    elif "TRANSFER" in deliver_content:
        _, sender, _, receiver, num = deliver_content.split()
        if balance[sender] < int(num):
            return
        else:
            balance[sender] -= int(num)
            balance[receiver] += int(num)
            show_bank()


def read_config(config_file):
    node_address_mapping = dict()
    with open(config_file, 'r') as f:
        node_num = int(f.readline().strip())
        content = f.readlines()
        for line in content:
            if 'node' in line:
                node_name, ip, port = line.split()
                node_address_mapping[node_name] = (ip, int(port))
    return node_num + 1, node_address_mapping


def tcp_connect(node_name, target_ip, target_port):
    global connect_number, node_socket_mapping
    while True:
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        if tcp_socket.connect_ex((target_ip, target_port)) == 0:
            connect_number_lock.acquire()
            connect_number += 1
            connect_number_lock.release()
            node_socket_mapping_lock.acquire()
            node_socket_mapping[node_name] = tcp_socket
            node_socket_mapping_lock.release()
            break


def tcp_listen(address):
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.bind(address)
    tcp_socket.listen(SOMAXCONN)
    return tcp_socket


def receive_msg_sub(input_socket):
    global cur_node_name, cur_queue, timestamp, node_socket_mapping, total_num
    while True:
        rec_content = input_socket.recv(2048).decode("utf-8")
        if len(rec_content) > 0:
            # print("--receive msg--")
            # print(rec_content)
            cur_queue_lock.acquire()
            # print("cur_queue")
            # for i in cur_queue.entries:
            #     print(i.get_message_string())
            # print("stream")
            for stream in rec_content.split('#')[:-1]:
                # print(stream)
                content, initial_ts, initial_node, cur_ts, cur_node, status = stream.split('@')
                status = int(status)
                initial_ts = int(initial_ts)
                cur_ts = int(cur_ts)
                msg = Message(content, initial_ts, initial_node, cur_ts, cur_node, status)

                if initial_node == cur_node_name:
                    stored_msg = cur_queue.get_msg(msg.label)
                    if (msg.cur_ts, int(msg.cur_node.split("node")[-1])) > (stored_msg.cur_ts, int(stored_msg.cur_node.split("node")[-1])):
                        new_msg = Message(content, initial_ts, initial_node, cur_ts, cur_node, stored_msg.status + 1)
                        cur_queue.update(new_msg)
                        while cur_queue.check_deliver():
                            deliver_queue_head()
                    else:
                        cur_queue.increase_status(msg.label)
                    # print("total num")
                    # print(total_num)
                    if cur_queue.get_status(msg.label) == total_num - 1:
                        sender_msg = cur_queue.get_msg(msg.label)
                        sender_msg.status = -1
                        multicast(sender_msg.get_message_string())
                else:
                    if status == -1:
                        cur_queue.update(msg)
                        while cur_queue.check_deliver():
                            deliver_queue_head()
                    else:
                        timestamp += 1
                        cur_msg = Message(content, initial_ts, initial_node, timestamp, cur_node_name, status)
                        cur_queue.enqueue(cur_msg)
                        # print("--send msg--")
                        # print(cur_msg.get_message_string())
                        try:
                            node_socket_mapping[initial_node].send(cur_msg.get_message_string().encode("utf-8"))
                        except:
                            node_socket_mapping[initial_node].close()
                            cur_queue_lock.release()
                            handle_failure(initial_node)
                            cur_queue_lock.acquire()
            cur_queue_lock.release()


def send_msg(node_name):
    global timestamp, cur_queue
    while True:
        for content in sys.stdin:
            if len(content) > 0:
                timestamp_lock.acquire()
                timestamp += 1
                cur_msg = Message(content, timestamp, node_name, timestamp, node_name, 0)
                timestamp_lock.release()
                cur_queue_lock.acquire()
                cur_queue.enqueue(cur_msg)
                cur_queue_lock.release()
                multicast(cur_msg.get_message_string())


def receive_msg(listen_socket):
    while True:
        cur_socket, _ = listen_socket.accept()
        receive_msg_sub_process = Thread(target=receive_msg_sub, args=(cur_socket,))
        receive_msg_sub_process.start()
        time.sleep(0.1)


def main():
    # TODO: set up all connections with other nodes

    # TODO: handle four inputs
    if len(sys.argv) != 4:
        raise Exception("The input parameters should be in form of node name, port, config file name")
    global cur_node_name, total_num
    cur_node_name = sys.argv[1]
    port = int(sys.argv[2])
    config_file = sys.argv[3]
    node_num, node_address_mapping = read_config(config_file)
    total_num = node_num
    listen_socket = tcp_listen(("localhost", port))
    for key, value in node_address_mapping.items():
        connect = Thread(target=tcp_connect, args=(key, value[0], value[1]))
        connect.start()
    time.sleep(5)
    receive = Thread(target=receive_msg, args=(listen_socket,))
    receive.start()
    while True:
        send_msg(cur_node_name)
    # return 0


if __name__ == '__main__':
    main()
