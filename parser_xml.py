import xml.etree.ElementTree as ET
import multiprocessing as mp
from commons_func import generate_new_node
from db_operation import *
from order_handle import process_order
lk = mp.Lock()

def process_create(root, response):
    for child in root:
      if child.tag == "account":
        try:
          add_account(child.attrib['id'], float(child.attrib['balance']))
          response.append(generate_new_node("created", None, {'id':str(child.attrib['id'])}))
        except Exception as e:
          response.append(generate_new_node("error", str(e), {'id':str(child.attrib['id'])}))
      elif child.tag == "symbol":
        if not child.attrib['sym']:
          response.append(generate_new_node("error", "Invalid symbol", {'sym':child.attrib['sym']}))
        else:
          for acct in child:
            try:
              #### AddPosition #####
              add_position(acct.attrib['id'], child.attrib['sym'], int(acct.text))
              response.append(generate_new_node("created", None, {'sym':child.attrib['sym'],'id':acct.attrib['id']}))
            except Exception as e:
              response.append(generate_new_node("error", str(e), {'sym':child.attrib['sym'],'id':acct.attrib['id']}))
    pass
  
def generate_transaction(root, child, response):
    if int(child.attrib['limit']) <= 0:
      response.append(generate_new_node("error", "Invalid limit price", {'id':str(root.attrib['id'])}))
      return
    print("getting lock")
    global lk
    with lk:
      print("adding transaction")
      tran_id = add_transaction(root.attrib['id'], child.attrib['sym'], int(child.attrib['amount']), float(child.attrib['limit']))
      process_order(tran_id)
    print("releasing lock")
    response.append(generate_new_node("opened", None, {'sym': child.attrib['sym'], 'amount':
                  str(int(child.attrib['amount'])), 'limit': str(child.attrib['limit']), 'id': str(tran_id)}))
    pass
  
def generate_query_transaction(root, child, response):
    session = Session()
    order = query_transaction(root.attrib['id'], int(child.attrib['id']), session)
    ###### might be wrong, maybe order.count() ######
    if len(order)==0:
      response.append(generate_new_node("error", "Invalid Transaction ID", {'id':str(child.attrib['id'])}))
      return
    else:
      status_node = ET.Element("status")
      status_node.set('id', child.attrib['id'])
      for p in order:
        if p.status_name == 'open':
          status_node.append(generate_new_node("open", None, {'shares': str(abs(p.shares))}))
        elif p.status_name == 'canceled':
          status_node.append(generate_new_node("canceled", None, {'shares': str(abs(p.shares)), 'time': str(p.time.timestamp())}))
        else:
          status_node.append(generate_new_node("executed", None, {'shares': str(abs(p.shares)), 'price': str(p.price), 'time': str(p.time.timestamp())}))
      response.append(status_node)
    session.close()
    pass
  
def generate_cancel_transaction(root, child, response):
  global lk
  with lk:
    session = Session()
    cancelled_node = ET.Element("canceled")
    cancelled_node.set('id', str(child.attrib['id']))
    try:
      order = cancel_transaction(root.attrib['id'], int(child.attrib['id']), session)
      for p in order:
        if p.status_name == 'open':
          cancelled_node.append(generate_new_node("open", None, {'shares': str(abs(p.shares))}))
        elif p.status_name == 'canceled':
          cancelled_node.append(generate_new_node("canceled", None, {'shares': str(abs(p.shares)), 'time': str(p.time.timestamp())}))
        else:
          cancelled_node.append(generate_new_node("executed", None, {'shares': str(abs(p.shares)), 'price': str(p.price), 'time': str(p.time.timestamp())}))
      response.append(cancelled_node)
    except Exception as e:
      response.append(generate_new_node("error", str(e), {'id':child.attrib['id']}))
    session.close()  
  pass

def process_transaction(root, response):
    print("entering process_transaction")
    if check_account(root.attrib['id']):
      for child in root:
        if child.tag == "order":
          print("processing order")
          generate_transaction(root, child, response)
        elif child.tag == "query":
          generate_query_transaction(root, child, response)
        else:
          generate_cancel_transaction(root, child, response)
    # except Exception as e:
    else:
      # Invalide_node = ET.Element("error")
      for child in root:
        response.append(generate_new_node("error", "Invalid Transaction ID", {'id':str(root.attrib['id'])}))
          
    pass

def parse_xml_req(req):
    root = ET.fromstring(req)
    response = ET.Element("result")
    if root.tag == "create":
      process_create(root, response)
      pass
    elif root.tag in ["transaction","transactions"]:
      print("parsing transaction")
      process_transaction(root, response)
      pass
    else:
      # raise ValueError(root.tag)
      response.text = "Invalid request"
    return ET.tostring(response).decode()