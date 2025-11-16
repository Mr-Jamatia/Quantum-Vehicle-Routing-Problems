from pygsp import graphs
import pygsp
import networkx as nx
import numpy as np

import math

from typing import Tuple, List

from ..Graph import Graph
from .vrprep_utils import loaddataset

class vrpRepGraph(Graph):
    """Generate the coordinates of 'n' instances (nodes)"""
    
    def __init__(self, file, seed = 1543):
        """
        Input:
            file: the location of xml graph file
            seed: used in the generation of a graph
        """
        self.graphFile = file
        self.nodelist = loaddataset(self.graphFile)
        self.n = len(self.nodelist.get_nodes()) + 1
        self.seed = seed
        self.set_seed()

    def set_seed(self, seed=None):
        np.random.seed(seed if seed else self.seed )

    def generate_graph(self) -> graphs.Graph:
        instance = np.zeros((self.n, self.n))
        coords = np.array([node.get_pos() for node in self.nodelist.get_all_nodes()])

        # Create the Weight Adjacency
        for x, points_A in enumerate(coords):
            for y, points_B in enumerate(coords):
                instance[x, y] = np.linalg.norm(points_A - points_B)
        
        np.fill_diagonal(instance, 0)

        # Define a Graph
        graph = graphs.Graph(instance)
        graph.set_coordinates(coords)

        self.graph = graph

        # Capacities
        self.nodeCapacities = [ node.get_dem() for node in self.nodelist.get_all_nodes() ]

        assert len(self.nodeCapacities) == len(coords) == self.n

        # Number of vehicles
        num_vehicles = math.ceil(sum(self.nodeCapacities) / self.nodelist._capacity)

        return graph


    def plotGraph(self):
        """
            Visualises the LogisticsGraph's graph object
        
        """
        pygsp.plotting.plot_graph(self.graph)
        input("Press any to continue")

        return

    def loadGraphPointsFromFile(self):
        raise NotImplementedError

    def loadGraphFromFile(self):
        raise NotImplementedError