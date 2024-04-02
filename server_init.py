import socket
from multiprocessing import Pool

###need change later####
from db_operation import *
from parser_xml import parse_xml_req

import collections
from parser_xml import lk
NUM_WORKERS = 3


def initialize_worker(lck):
    ###need change later####
    engine.dispose(close = False)
    
    global lock
    lock = lck 
    pass

def rcv_xml_length(ck):
    recived_data = ""
    while True:
      chunk = ck.recv(1).decode("utf-8")
      if chunk == "\n":
          break
      recived_data += chunk
    if not recived_data:
      raise ValueError("No data received")
    try:
      recived_num = int(recived_data)
    except ValueError:
      raise ValueError("Invalid data received")
    if recived_num <= 0:
      raise ValueError("Invalid data received for length")
    return recived_num

def rcv_prcs_xml_from_ck(ck):
  # recived_data = ""
  try:
    # return recived_num
    recived_num = rcv_xml_length(ck)
    xml_data = ck.recv(recived_num).decode("utf-8")
    print("Received data: ", xml_data)
    response = parse_xml_req(xml_data)
    ck.sendall(response.encode("utf-8"))
    ck.close()
  except Exception as e:
    ck.sendall(str(e))
    ck.close()

def sk_connect():
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sk.bind(("0.0.0.0",12345))
    print("Server is listening on port 12345")
    sk.listen(100)
    return sk
    

def server_init():
    drop_all_and_init()
    pool = Pool(processes=NUM_WORKERS, initializer=initialize_worker, initargs=(lk,))
    # create a db here first
    ########################
    sk = sk_connect()
    csk_lst = collections.deque()
    while True:
        csk, addr = sk.accept()
        print("Connection from: ", addr)
        csk_lst.append(csk)
        if csk_lst:
          ccsk = csk_lst.popleft()
          
          pool.apply_async(func=rcv_prcs_xml_from_ck, args=(ccsk,))
          
          print("Connection closed")
          

if __name__ == "__main__":
     server_init()