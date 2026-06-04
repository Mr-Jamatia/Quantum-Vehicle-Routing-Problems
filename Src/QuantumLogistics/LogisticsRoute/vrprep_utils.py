import xml.etree.ElementTree as ET
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def loaddataset(filename='dataset/CMT01.xml'):
  tree = ET.parse(filename)
  root = tree.getroot()

  capacity = float(root.findall('.//capacity')[0].text)   # All vehicles have the same capacity
  nodes = NodeList(capacity)

  nodes.vehicle = {
    "departure_node": int(list(root.find('fleet'))[0].find('departure_node').text),
    "arrival_node": int(list(root.find('fleet'))[0].find('arrival_node').text),
    "capacity": float(list(root.find('fleet'))[0].find('capacity').text),
  }


  # nodes.vehicle = {
  #   "departure_node": int(root.find('fleet').getchildren()[0].find('departure_node').text),
  #   "arrival_node": int(root.find('fleet').getchildren()[0].find('arrival_node').text),
  #   "capacity": float(root.find('fleet').getchildren()[0].find('capacity').text),
  # }


  for index, node in enumerate(root.iter('vehicle_profile')):
    assert node.find('arrival_node').text == node.find('departure_node').text
    id_ = int(node.find('arrival_node').text)
    demand = float(node.find('capacity').text)
    depot_node = [ n for n in root.iter('node') if int(n.get('id')) == id_ ][0]
    x = float(depot_node.find('cx').text)
    y = float(depot_node.find('cy').text)
    position = np.array([x, y])
    depot = Node(id_, 0, position, demand)
    nodes.append(depot)
    
    nodes.vehicle = {
      "departure_node": index,
      "arrival_node": index,
      "capacity": demand,
    }

  for request in root.iter('request'):
    node = [ n for n in root.iter('node') if int(n.get('id')) == int(request.attrib['node']) ][0]
    id_ = int(node.get('id'))
    type_ = int(node.get('type'))
    x = float(node.find('cx').text)
    y = float(node.find('cy').text)
    position = np.array([x, y])
    demand = float(request.find('quantity').text)
    node_ = Node(id_, type_, position, demand)
    nodes.append(node_)
  

  return nodes


class Node(object):

  def __init__(self, id_, type_, position, demand):
    self._id = id_
    self._type = type_
    self._position = position
    self._demand = demand

  # Getter
  def get_id(self):
    return self._id

  def get_type(self):
    return self._type

  def get_pos(self):
    return self._position

  def get_dem(self):
    return self._demand

class NodeList(list):
  def __init__(self, capacity):
    list.__init__(self)
    self._capacity = capacity
    self._depot = None
    self._is_first_get_depot = True
    self.vehicle = Node

  def get_depot(self):
    if self._is_first_get_depot:
      if 0 not in [ n.get_type() for n in self ]:
          self[0]._type = 0
      for node in self:
        if node.get_type() == 0:
          self._depot = node
          self._is_first_get_depot = False
          return self._depot
    return self._depot

  def get_nodes(self):
    return [node for node in self if node.get_type()==1]
  
  def get_all_nodes(self):
    return self # sorted([node for node in self], key=lambda n: n._id)

  def get_nodes_id_list(self):
    return [node.get_id() for node in self if node.get_type()==1]

  def get_node_pos_from_id(self, id_):
    for node in self:
      if node.get_id() == id_:
        return node.get_pos()

  def is_feasible(self, route):
    amount = 0
    for node in self:
      if node.get_id() in route:
        amount += node.get_dem()
    is_feasible = (amount < self._capacity)
    return is_feasible
