from pygsp import graphs
import pygsp
import networkx as nx
import numpy as np

from typing import Tuple, List

class Graph:
    """Generate the coordinates of 'n' instances (nodes)"""

    def set_seed(self, seed=None):
        np.random.seed(seed if seed else self.seed )
    

    def generate_graph(self) -> graphs.Graph:
        raise NotImplementedError()

    def plotGraph(self):
        raise NotImplementedError()
