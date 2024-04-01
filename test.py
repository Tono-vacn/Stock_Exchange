from parser_xml import *
from server_init import *
from db_operation import *
import time

def testdb_operation():
  add_account('test1', 1000)
  add_account('test2', 1000)
  add_account('test3', 1000)
  add_account('test4', 1000)
  print("check account")
  
  
  add_position('test1', 'AAPL', 20)
  add_position('test2', 'AAPL', 10)
  add_position('test3', 'AAPL', 10)
  add_position('test4', 'MSFT', 10)
  add_position('test4', 'AAPL', 10)
  
  print("check position")
  
  add_transaction('test1', 'AAPL', 5, 90)
  add_transaction('test2', 'AAPL', -10, 100)
  add_transaction('test3', 'AAPL', 10, 100)
  add_transaction('test4', 'MSFT', -10, 100)
  
  print("check transaction")
  
def testParse():
    print("----Test 1 Failed: Account exist is 0, balance is negative, account does not exist----")
    xmlString = "<create><account id=\"0\" balance=\"50000\"/><account id=\"2\" balance=\"-100000\"/><symbol sym=\"TESLA\"><account id=\"1\">200</account></symbol></create>"
    print("Request:")
    print(xmlString)
    print("Response:")
    print(parse_xml_req(xmlString))
    print("")
    
def testParse_succ():
    print("----Test 4 Success: Open a order, query it, then delete it and query again----")
    xmlString4 = "<create><account id=\"2\" balance=\"50000\"/><symbol sym=\"TB\"><account id=\"2\">500</account></symbol></create>"
    xmlString5 = "<transactions id=\"2\"><order sym=\"TESLA\" amount=\"100\" limit=\"250\"/><order sym=\"TB\" amount=\"-100\" limit=\"120\"/><query id=\"1\"/><query id=\"2\"/></transactions>"
    xmlString6 = "<transactions id=\"2\"><query id=\"1\"/></transactions>"
    xmlString9 = "<transactions id=\"2\"><cancel id=\"1\"/><cancel id=\"2\"/><query id=\"1\"/><query id=\"2\"/></transactions>"
    print("Request:")
    print(xmlString4)
    print(xmlString5)
    print(xmlString6)
    print(xmlString9)
    print("Response:")
    print(parse_xml_req(xmlString4))
    print(parse_xml_req(xmlString5))
    time.sleep(1)
    # addStatus(  1, 'executed', 50, 250, getCurrentTime())
    # print(parsing_XML(  xmlString6)
    time.sleep(1)
    print(parse_xml_req(xmlString9))
    # session.close()
  
if __name__=='__main__':
  drop_all_and_init()
  
  ####test1####
  # testdb_operation()
  # process_order(1)
  # process_order(2)
  # try:
  #   cancel_transaction('test1', 1)
  # except Exception as e:
  #   print(e,1)
  # try:
  #   cancel_transaction('test2', 2)
  # except Exception as e:
  #   print(e,2)
  # try:
  #   cancel_transaction('test3', 3)
  # except Exception as e:
  #   print(e,3)
  
  # cancel_transaction('test4', 4)
  
  # process_order(3)
  
  ####test2####
  testParse_succ()
  
  
