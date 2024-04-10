#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import socket
import time
import threading
import sys
sys.path.append("./")

from commons_func import generate_new_node
SERVER_ADDR = '0.0.0.0'
USER_NUM = 10
serial_concurrent_flag = False 
# True for serialize, False for concurrent
print_flag = True

def createRequest(uid, balance, position:dict):
    uid = str(uid)
    balance = str(balance)
    root = ET.Element("create")
    account_node = ET.Element("account")
    account_node.set("id", uid)
    account_node.set("balance", balance)
    root.append(account_node)
    for sym, num in position.items():
        symbol_node = generate_new_node("symbol", None, {"sym": str(sym), })
        symbol_node.append(generate_new_node("account", str(num), {"id": uid, }))
        root.append(symbol_node)
    return (str(len(ET.tostring(root))) + "\n" + str(ET.tostring(root).decode())).encode("utf-8")


def transactionRequest(uid, order, query, cancel):
    uid = str(uid)
    root = ET.Element("transactions")
    root.set("id", uid)
    if order:
        for sym, amt, limit in order:
            root.append(generate_new_node("order", None, {"sym": str(sym), "amount": str(amt), "limit": str(limit)}))
    if query:
        for tid in query:
            root.append(generate_new_node("query", None, {"id": str(tid), }))
    if cancel:
        for tid in cancel:
            root.append(generate_new_node("cancel", None, {"id": str(tid), }))
    return (str(len(ET.tostring(root))) + "\n" + str(ET.tostring(root).decode())).encode("utf-8")


def get_transc_id(response):
    root = ET.fromstring(response)
    for child in root:
        if child.tag == 'opened':
            return child.attrib['id']
    return None


'''
@func: client connect to the server and send the request
@param: encoded request
'''
def set_socket():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (SERVER_ADDR, 12345)
    client_socket.connect(server_address)
    return client_socket

def client_send(request):
    client_socket = set_socket()
    client_socket.sendall(request)
    print(f"Request send {request}") if print_flag else None
    response = client_socket.recv(1024)
    print('Received data:', response) if print_flag else None
    client_socket.close()
    return response.decode("utf-8")


def complexTest(id):
    client_send(createRequest(id, 10000, {"AAPL": 0, "MSFT": 100}))
    response = client_send(transactionRequest(id, [("MSFT", -100, 100)], [], []))
    response1 = client_send(transactionRequest(id, [("AAPL", 50, 100)], [], []))
    response2 = client_send(transactionRequest(id, [("AAPL", 50, 100)], [], []))
    client_send(transactionRequest(id, [], [get_transc_id(response), get_transc_id(response1), get_transc_id(response2)], [get_transc_id(response)]))
    
def simpleTest(id):
    client_send(createRequest(id, 0, {"AAPL": 100, }))
    response = client_send(transactionRequest(id, [("AAPL", -100, 100)], [], []))
    client_send(transactionRequest(id, [], [get_transc_id(response), ], []))

def TestCreation(id):
    complexTest(id) if id % 2 == 1 else simpleTest(id)

def serializeTest(number):
    for i in range(1, number + 1):
        TestCreation(i)


def concurrentTest(number):
    thread_list = list()
    for i in range(1, number+1):
        t = threading.Thread(target=TestCreation, args=(i, ))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()


if __name__ == "__main__":
    start_time = time.time()
    serializeTest(USER_NUM) if serial_concurrent_flag else concurrentTest(USER_NUM)
    end_time = time.time()

    print(f"Running time is {end_time - start_time}")