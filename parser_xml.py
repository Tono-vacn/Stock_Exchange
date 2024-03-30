import xml.etree.ElementTree as ET
import multiprocessing as mp
from commons_func import generate_new_node
from adddb import addAccount
lk = mp.Lock()

def process_create(root, response):
    for child in root:
      if child.tag == "account":
        try:
          addAccount(int(child.attrib['id']), float(child.attrib['balance']))
          response.append(generate_new_node("created", None, {'id':child.attrib['id']}))
        except Exception as e:
          response.append(generate_new_node("error", str(e), {'id':child.attrib['id']}))
      elif child.tag == "symbol":
        if not child.attrib['sym']:
          response.append(generate_new_node("error", "Invalid symbol", {'sym':child.attrib['sym']}))
        else:
          for acct in child:
            try:
              #### AddPosition #####
              addPosition(int(acct.attrib['id']), child.attrib['sym'], int(acct.text))
              response.append(generate_new_node("created", None, {'sym':child.attrib['sym'],'id':acct.attrib['id']}))
            except Exception as e:
              response.append(generate_new_node("error", str(e), {'sym':child.attrib['sym'],'id':acct.attrib['id']}))
    pass
  
def process_transaction(root, response):
    pass

def parse_xml_req(req):
    root = ET.fromstring(req)
    response = ET.Element("result")
    if root.tag == "create":
      process_create(root, response)
      pass
    elif root.tag == "transaction":
      pass
    else:
      response.text = "Invalid request"
    return ET.tostring(response).decode()