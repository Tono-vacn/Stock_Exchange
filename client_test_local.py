#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import socket
import time
import threading
SERVER_ADDR = 'localhost'
USER_NUM = 10
set_concurrent = False
set_serialize = True
set_print = True

'''
This file is for scalability testing, including the serialize test and concurrent test
Please feel free to adjust the server address, user number, concurrent or serialize above
'''


'''
* @func: Construct an element node
* @param: {Msg, **attributes} Msg is the message, attributes are a set of key-value pair
* @return: {child_node} node to be append
'''


def construct_node(Name, Msg, **attributes):
    child_node = ET.Element(Name)
    if Msg:
        child_node.text = Msg
    for key, value in attributes.items():
        child_node.set(key, value)
    return child_node


'''
@func: Construct a <create> request for client
@param: uid: user account id wants to create;
        balance: The balance for this user
        position: {symbol:num, symbol:num}The position to be added to the specified account
@return: <create> request encoded in utf-8
'''


def createRequest(uid, balance, position):
    uid = str(uid)
    balance = str(balance)
    root = ET.Element("create")
    account_node = ET.Element("account")
    account_node.set("id", uid)
    account_node.set("balance", balance)
    root.append(account_node)
    for sym, num in position.items():
        sym = str(sym)
        num = str(num)
        symbol_node = construct_node("symbol", None, **{"sym": sym, })
        symbol_node.append(construct_node(
            "account", num, **{"id": uid, }))
        root.append(symbol_node)
    request = str(len(ET.tostring(root))) + "\n" + \
        str(ET.tostring(root).decode())
    return request.encode("utf-8")


'''
@func: Construct a <transaction> request for client
@param: uid: user account id to query;
        order: a set of order tuples including sym, amt, limit [(s1,a1,l1),(s2, a2,l2)]
        query: a set of query tuples, including the transaction id, [1,2,3,4]
        cancle: a set of cancel tuples, including the transaction id, [1,2,3,4]
@return: <transaction> request encoded in utf-8
'''


def transactionRequest(uid, order, query, cancel):
    uid = str(uid)
    root = ET.Element("transactions")
    root.set("id", uid)
    if order:
        for sym, amt, limit in order:
            root.append(construct_node("order", None, **
                        {"sym": str(sym), "amount": str(amt), "limit": str(limit)}))
    if query:
        for tid in query:
            root.append(construct_node("query", None, **{"id": str(tid), }))
    if cancel:
        for tid in cancel:
            root.append(construct_node("cancel", None, **{"id": str(tid), }))
    request = str(len(ET.tostring(root))) + "\n" + \
        str(ET.tostring(root).decode())
    return request.encode("utf-8")


def ParseTid(response):
    root = ET.fromstring(response)
    for child in root:
        if child.tag == 'opened':
            return child.attrib['id']
    return None


'''
@func: client connect to the server and send the request
@param: encoded request
'''


def client_send(request):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # connect the socket to a specific address and port
    server_address = (SERVER_ADDR, 12345)
    client_socket.connect(server_address)
    client_socket.sendall(request)
    if set_print:
        print(f"Request send {request}")
    # receive data from server
    response = client_socket.recv(1024)
    if set_print:
        print('Received data:', response)
    # print()
    # close the connection
    client_socket.close()
    return response.decode("utf-8")


def TestCreation(id):
    if id % 2 == 1:
        tid_list = list()
        # If the user is odd, construct buy orders
        client_send(createRequest(id, 10000, {"TELSA": 0, "X": 100}))
        # print()
        response = client_send(transactionRequest(
            id, [("X", -100, 100)], [], []))
        # print(response)
        cancel_id = ParseTid(response)
        response = client_send(transactionRequest(
            id, [("TELSA", 50, 100)], [], []))
        # print(response)
        tid_list.append(ParseTid(response))
        response = client_send(transactionRequest(
            id, [("TELSA", 50, 100)], [], []))
        # print(response)
        tid_list.append(ParseTid(response))
        client_send(transactionRequest(
            id, [], [cancel_id, tid_list.pop(0), tid_list.pop(0)], [cancel_id, ]))
        # print()
    else:
        # If the user is even number construct sell order
        client_send(createRequest(id, 0, {"TELSA": 100, }))
        # print()
        response = client_send(transactionRequest(
            id, [("TELSA", -100, 100)], [], []))
        # print(response)
        tid = ParseTid(response)
        client_send(transactionRequest(
            id, [], [tid, ], []))
        # print()


def TestQuery(id):
    tid_list = list()
    client_send(createRequest(id, 10000, {"X": 100, "Y": 100}))
    response = client_send(transactionRequest(
        id, [("X", 100, 100)], [], []))
    # print()
    # print(response)
    tid_list.append(ParseTid(response))
    response = client_send(transactionRequest(
        id, [("Y", -100, 100)], [], []))
    # print(response)
    tid_list.append(ParseTid(response))
    # print()
    client_send(transactionRequest(
        id, [], [tid_list[0], tid_list[1]], [tid_list[0], tid_list[1]]))
    client_send(transactionRequest(
        id, [], [tid_list[0], tid_list[1]], []))
    # print()


def serializeTest(number):
    for i in range(1, number + 1):
        TestCreation(i)


def concurrentTest(number):
    thread_list = list()
    for i in range(1, number+1):
        t = threading.Thread(target=TestCreation, args=(i, ))
        # t = threading.Thread(target=TestQuery, args=(i,))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()


if __name__ == "__main__":
    start_time = time.time()
    if set_serialize:
        serializeTest(USER_NUM)
    if set_concurrent:
        concurrentTest(USER_NUM)
    end_time = time.time()

    print(f"Running time is {end_time - start_time}")