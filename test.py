from parser_xml import *
from server_init import *
from db_operation import *
from server_init import *
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
    print(parse_xml_req(xmlString6))
    time.sleep(1)
    print(parse_xml_req(xmlString9))
    # session.close()
    
def testParse_fail():
  print("----Test 1 Failed: Account exist is 0, balance is negative, account does not exist----")
  xmlString = "<create><account id=\"0\" balance=\"50000\"/><account id=\"2\" balance=\"-100000\"/><symbol sym=\"TESLA\"><account id=\"1\">200</account></symbol></create>"
  print("Request:")
  print(xmlString)
  print("Response:")
  print(parse_xml_req(xmlString))
  print("")
  print("----Test 2 Failed: Query number and cancel number does not exist----")
  xmlString2 = "<create><account id=\"1\" balance=\"50000\"/><symbol sym=\"TESLA\"><account id=\"1\">500</account></symbol></create>"
  xmlString3 = "<transactions id=\"1\"><query id=\"1\"/><cancel id=\"1\"/></transactions>"
  print("Request:")
  print(xmlString2)
  print(xmlString3)
  print("Response:")
  print(parse_xml_req(xmlString2))
  print(parse_xml_req(xmlString3))
  print("")
  print("----Test 3 Failed: Trasaciton account id doesn't exsit, transcation doesn't belong to account----")
  xmlString8 = "<transactions id=\"1000\"><order sym=\"TESLA\" amount=\"100\" limit=\"250\"/><query id=\"1\"/><cancel id=\"1\"/></transactions>"
  xmlString7 = "<transactions id=\"1\"><cancel id=\"1\"/><query id=\"1\"/></transactions>"
  print("Request:")
  print(xmlString8)
  print(xmlString7)
  print("Response:")
  print(parse_xml_req(xmlString8))
  print(parse_xml_req(xmlString7))
  print("")
  
def testParseMatch():
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    print("----Test 1----")
    xmlString = "<create><account id=\"1\" balance=\"100000\"/><account id=\"2\" balance=\"100000\"/><account id=\"3\" balance=\"100000\"/><account id=\"4\" balance=\"100000\"/><account id=\"5\" balance=\"100000\"/><account id=\"6\" balance=\"100000\"/><account id=\"7\" balance=\"100000\"/>"
    xmlString += "<symbol sym=\"X\"><account id=\"1\">500</account><account id=\"2\">500</account><account id=\"3\">500</account><account id=\"4\">500</account><account id=\"5\">500</account><account id=\"6\">500</account><account id=\"7\">500</account></symbol></create>"
    xmlString1 = "<transactions id=\"1\"><order sym=\"X\" amount=\"300\" limit=\"125\"/></transactions>"
    xmlString2 = "<transactions id=\"2\"><order sym=\"X\" amount=\"-100\" limit=\"130\"/></transactions>"
    xmlString3 = "<transactions id=\"3\"><order sym=\"X\" amount=\"200\" limit=\"127\"/></transactions>"
    xmlString4 = "<transactions id=\"4\"><order sym=\"X\" amount=\"-500\" limit=\"128\"/></transactions>"
    xmlString5 = "<transactions id=\"5\"><order sym=\"X\" amount=\"-200\" limit=\"140\"/></transactions>"
    xmlString6 = "<transactions id=\"6\"><order sym=\"X\" amount=\"400\" limit=\"125\"/></transactions>"
    xmlString7 = "<transactions id=\"7\"><order sym=\"X\" amount=\"-400\" limit=\"124\"/></transactions>"

    print(xmlString)
    print(parse_xml_req(xmlString))
    print(xmlString1)
    print(parse_xml_req(xmlString1))
    print(xmlString2)
    print(parse_xml_req(xmlString2))
    print(xmlString3)
    print(parse_xml_req(xmlString3))
    print(xmlString4)
    print(parse_xml_req(xmlString4))
    print(xmlString5)
    print(parse_xml_req(xmlString5))
    print(xmlString6)
    print(parse_xml_req(xmlString6))
    print(xmlString7)
    print(parse_xml_req(xmlString7))
    
    
def testCancel():
    xmlString4 = "<create><account id=\"2\" balance=\"50000\"/><symbol sym=\"TB\"><account id=\"2\">500</account></symbol></create>"
    xmlString5 = "<transactions id=\"2\"><order sym=\"TESLA\" amount=\"100\" limit=\"250\"/><order sym=\"TB\" amount=\"-100\" limit=\"120\"/><query id=\"1\"/><query id=\"2\"/></transactions>"
    xmlString6 = "<transactions id=\"2\"><cancel id=\"1\"/><cancel id=\"2\"/><query id=\"1\"/></transactions>"
    xmlString9 = "<transactions id=\"2\"><cancel id=\"1\"/><cancel id=\"2\"/><query id=\"1\"/><query id=\"2\"/></transactions>"
    print("Request:")
    print(xmlString4)
    print(" ")
    print(xmlString5)
    print(" ")    
    print(xmlString6)
    print(" ")
    print(xmlString9)
    print(" ")
    print("Response:")
    print(parse_xml_req(xmlString4))
    print(parse_xml_req(xmlString5))
    print(parse_xml_req(xmlString6))
    print(parse_xml_req(xmlString9))
    
def testSocket():
    server_init()

if __name__=='__main__':
  # drop_all_and_init()
  
  server_init()
  
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
  # testParse_succ()
  # testParse_fail()
  
  ####test3####
  # testParseMatch()
  # testCancel()
  
  
