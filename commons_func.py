import xml.etree.ElementTree as ET
from datetime import datetime

def get_now_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_new_node(tag, text, attr:dict):
    new_node = ET.Element(tag)
    if text:
        new_node.text = text
    if attr:
      for k,v in attr.items():
        new_node.set(k,v)
    return new_node