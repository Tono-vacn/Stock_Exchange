import socket
import time

import sys

sys.path.append("./")

from testing.scalability.client_test_local import createRequest, transactionRequest

'''
This is the client indivitual test for handleing serializable small amount request;
For the concurrent large scalability test please go the client_test.py
'''


def client_send(request):
    # create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # connect the socket to a specific address and port
    server_address = ('localhost', 12345)
    client_socket.connect(server_address)
    print('Connected to', server_address)
    # request = "142\n<create><account id=\"1\" balance=\"50000\"/><account id=\"2\" balance=\"100000\"/><symbol sym=\"TESLA\"><account id=\"1\">200</account></symbol></create>"
    client_socket.sendall(request)
    print("Request sent")
    # receive data from server
    response = client_socket.recv(1024)
    print('Received data:', response)
    # close the connection
    client_socket.close()


# def constructOrderString(id, args):
#     print(args.key(), args.value())
#     return f'<transactions id=\"{id}\"><order sym=\"X\" amount=\"300\" limit=\"125\"/></transactions>'

def constructRequestLength(request):
    new_request = str(len(request))+"\n"+request
    return new_request.encode("utf-8")


if __name__ == '__main__':
    start_time = time.time()
    # xmlString = "<create><account id=\"1\" balance=\"10000000\"/><account id=\"2\" balance=\"10000000\"/><symbol sym=\"X\"><account id=\"1\">1000000</account><account id=\"2\">10000000</account></symbol></create>"
    # client_send(constructRequestLength(xmlString))
    # xmlString1 = "<transactions id=\"1\"><order sym=\"X\" amount=\"10\" limit=\"12\"/></transactions>"
    # client_send(constructRequestLength(xmlString1))
    # xmlString2 = "<transactions id=\"1\"><order sym=\"X\" amount=\"-10\" limit=\"10\"/></transactions>"
    # client_send(constructRequestLength(xmlString2))
    client_send(createRequest(1, 2000, {"AAPL": 2000, "X": 1000}))
    client_send(transactionRequest(1, [("AAPL", 10, 10), ("X", -10, 5)], [1, 2], None))
    client_send(transactionRequest(1, None, None, [1, 2]))
    client_send(transactionRequest(1, None, [1, 2], None))
    end_time = time.time()
    print(f"finish time is {end_time-start_time}")
    # xmlString2 = "<transactions id=\"2\"><order sym=\"X\" amount=\"-10\" limit=\"2\"/></transactions>"
    # client_send(xmlString2)