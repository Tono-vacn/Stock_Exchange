import xml.etree.ElementTree as ET
import multiprocessing as mp
from commons_func import generate_new_node
lk = mp.Lock()

def process_create(root, response):
    for child in root:
      if child.tag == "account":
        # add_account(child, response)
        response.append(generate_new_node("created", None, {'id':child.attrib['id']}))
    pass
  
def process_transaction(root, response):
    pass

def parse_xml_req(req):
    root = ET.fromstring(req)
    response = ET.Element("result")
    if root.tag == "create":
      pass
    elif root.tag == "transaction":
      pass
    else:
      response.text = "Invalid request"
    return ET.tostring(response).decode()