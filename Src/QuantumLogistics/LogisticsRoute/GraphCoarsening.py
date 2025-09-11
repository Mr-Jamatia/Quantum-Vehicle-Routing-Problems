from abc import ABC, abstractclassmethod
import math
import networkx as nx
import pygsp
import matplotlib.pyplot as plt
import numpy as np

from graph_coarsening import coarsening_utils
from graph_coarsening.coarsening_utils import *

import graph_coarsening.graph_utils


class CoarseningEngine(ABC):

    def __init__(self):
        """
            General coarsening Engine Class used to coarsen Logistics Graphs in VRP problem
        """
        # ratio of coarse nodes to fine nodes
        self.rate = 1

        return

    @abstractclassmethod
    def coarsen(self):

        raise NotImplementedError




class BlankCoarseningEngine:
    def __init__(self):
        """
            General coarsening Engine Class used to coarsen Logistics Graphs in VRP problem
        """

        return


    def coarsen(self):
        print("Using blank coarsening engine, no coarsening algorithm defined")
        return








class DeltaCoarseningEngine:

    def __init__(self, coarsenRate = 0.1, radiusCoefficient = 0.2):
        """
            General coarsening Engine Class used to coarsen Logistics Graphs in VRP problem

        Args:
            coarsening_ration (float, optional): The size of the graph we are interested in preserving. Defaults to 0.2.
            kmax (float, optional): The size of the subspace we are interested in preserving. Defaults to 0.2.
            method (str, optional): The method of coarsening. Defaults to 'nearest'.

        """

        # self.edl.values
        self.rate = coarsenRate
        self.radiusCoefficient = radiusCoefficient

        return







    def coarsen(self, graph, depot, nodeWeights, maxCapacity):
        """
            Accepts a LogisticsRoute object
            Returns:
                Coarse graph object 
                Fine to coarse node mapping

            # This currently only handles a single depot - needs to be modified to handle multiple
        """
        self.graph = graph
        self.graphWeights = nodeWeights
        self.depot = [depot]
        self.maxCapacity = maxCapacity

        #TODO: Is there any reason this is using networkx? Need to move towards a consistent graph package
        # Better to remove depot node from network and go from adjacency matrix
        self.G = nx.from_numpy_array(self.graph.W.todense())
        self.edgList = { e:self.G.get_edge_data(*e)['weight'] for e in self.G.edges}
        tempEdgList = self.edgList.copy()

        # removing edges to 0:
        for key in list(tempEdgList.keys()):
            if 0 in key:
                tempEdgList.pop(key)

        pairsToCoarsen = []
        bounds = 1
        whileCounter = 0

        while len(pairsToCoarsen) == 0 and whileCounter < 10:
            # get coarsening radius
            coarseningRadius = self.generateCoarseningRadius(tempEdgList, bounds*self.radiusCoefficient)

            # print("\n\n\n")
            # print("COARSENING NEW GRAPH")
            # print("Coarsening Radius :", coarseningRadius)
            
            # identify node pairs that can be coarsened in graph
            pairsToCoarsen = self.identifyCoarseningPairs(coarseningRadius)

            # adjusting bouds if no pairs found
            bounds = 1.4 * bounds

            whileCounter += 1


        # Coarsen Graph - what is the point of this if everything gets overwritten anyway?
        coarseningMatrix, coarseGraph = self.generateCoarseGraph(pairsToCoarsen)

        plotCoords = False
        if plotCoords == True:
            #print(coarseGraph.coords)
            plt.scatter(coarseGraph.coords[:,0], coarseGraph.coords[:,1])
            plt.scatter(self.graph.coords[:,0], self.graph.coords[:,1])
            plt.show()

        return coarseGraph, coarseningMatrix







    def generateCoarseGraph(self, nodePairsToCoarsen):
        """
            Generates a coarse graph for a SINGLE STEP of coarsening
            C : np.array of size n x N
                The coarsening matrix. Maps n coarse nodes to N fine nodes using formula in Loukas
            Gc : pygsp Graph
                The smaller graph.
        """

        G = self.graph #the original graph
        GAdjacency = G.W

        # Creating coarsening matrix based on pairs of nodes to contract
        C = get_coarsening_matrix(G, nodePairsToCoarsen)                       # level n to level n-1 coarsening Matrix 

        #print(C)

        # Coarse Graph Coords:
        coarseCoords = coarsen_vector(G.coords, C)

        # Coarse Adjacency
        # Generating a Loukas coarse graph to get a binary adjacency for connectivity:
        Wc = graph_utils.zero_diag(coarsen_matrix(GAdjacency, C))              # coarsen and remove self-loops
        Wc = (Wc + Wc.T) / 2                                                    # this is only needed to avoid pygsp complaining for tiny errors
        
        # constructing own W:
        nodeNum = coarseCoords.shape[0]
        adj = Wc
        distanceAdja = np.zeros((nodeNum, nodeNum))
        for pointIdx1 in range(nodeNum):
            for pointIdx2 in range(pointIdx1 + 1,  nodeNum):
                if adj[pointIdx1, pointIdx2] != 0:
                    dist = np.linalg.norm(coarseCoords[pointIdx1] - coarseCoords[pointIdx2])
                    distanceAdja[pointIdx1, pointIdx2] = dist
                    distanceAdja[pointIdx2, pointIdx1] = dist


        # Making new coarse graph
        #Gc = gsp.graphs.Graph(Wc, coords=coarsen_vector(G.coords, iC))          # Some Variable
        Gc = gsp.graphs.Graph(distanceAdja, coords=coarseCoords)                # New euclidean coarse graph

       # Coarsening Matrix
        # In multilevel coarsening must propogate coarsening matrix:
        # C = sp.sparse.eye(G.N, format="csc")                                    # Some Variable            
        # C = iC.dot(C)                                                           # full coarsening matrix

        return C, Gc



    def generateCoarseningRadius(self, edgList, partitionCoefficient):
        """
            Returns the radius under which nodes are coarsened
            Based on parition weights
        """
        # TODO : FIXIT ?
        '''
        (1,2): 2.1,
        (2,1): 5.1,
        '''
        partition = partitionCoefficient 

        w = list(edgList.values())
        w = list(sorted(w))

        size = self.G.number_of_nodes() # 20
        #size = self.G.N # 20
        part = math.floor(size * partition) # 4

        coarseningRadius = (w[part] + w[part+1]) / 2

        return coarseningRadius




    def identifyCoarseningPairs(self, coarseningRadius):
        """
            Used to identify subgraphs to contract during coarsening
        """
        self.visited = []
        self.collapse = []

        # order nodes based on weights (minimum weight first)
        sortedIdxs = np.argsort(self.graphWeights)

        for n in sortedIdxs: 
        #for n in self.G.nodes:
            if n not in self.visited:
                self.check_collapsable(n, self.edgList, coarseningRadius)

        return self.collapse




    def check_collapsable(self, curr, edgList, coarseningRadius, debug=False):
        """
            curr - current node being checked
            edgList - list of edge lengths
        """
        # TODO : Avoid 2 neghbourin... colla..

        # If the current node has been 
        if curr in self.visited:
            return

        neighbours = self.getNeighbourData(curr, edgList)

        # Possible speed up?
        for nodes, weight in neighbours.items():
            a,b = nodes
            coarsenedNodeCapacity = self.graphWeights[a] + self.graphWeights[b]
            # Checks the followiung:
                # If edge is small enough to contract
                # If a nd b not the depot (cannot contract the depot)
                # A and B have not already been coarsened/attached to a coarsened node
                # the combined capacity of a coarsened a+b node is less than the capacity of a given truck

            if weight < coarseningRadius and (a not in self.depot and b not in self.depot) and (a not in self.visited and b not in self.visited) and (coarsenedNodeCapacity < self.maxCapacity):
                self.collapse += [ nodes ]
                self.visited += [ *nodes ]

                # adding all neigbour nodes of a and b to visited
                for node in nodes:
                    listOfNeigbours = [k for v,k in self.getNeighbourData(node, edgList).keys()]
                    self.visited += [ *listOfNeigbours ]

                if debug:
                    print( f"[+] curr : {curr}", neighbours )
                    print(f"Adding Nodes: {nodes}")
                    print(f'updated visitedList: {self.visited}')
                    print("\n")

                return

        self.visited += [ curr ]

        if debug:
            print( f"[ ] curr : {curr}", neighbours )
            print(f'updated visitedList: {self.visited}')
            print("\n")

        for nodes in set([ i for n in list(neighbours.keys()) for i in n ]):
            self.check_collapsable(nodes, edgList, coarseningRadius)

        return



    def getNeighbourData(self, node, edgList):
        # Finds all neighbours who have not been visited
        # Returns a dict of {(node, neighbourNode):edgeWeight}
        
        neighbour_data = {}

        size = self.graph.N
        for ConNode in range(size):
            if ConNode not in self.visited:
                edgBase = (node, ConNode)
                edg = edgBase
                if ConNode < node:
                    edg = (ConNode, node)

                if edg in edgList:
                    neighbour_data[edgBase] = edgList[edg]

        # sorted on value
        neighbours = dict(sorted(neighbour_data.items(), key=lambda item: item[1]))

        return neighbours





    def inflateSolution(self, solution, fineGraph, coarseningMatrix):
        """
            coarseSolution      - [[(0,1), (1,5), (5,0)], [(0,2), (2, 4), (4, 0)] sequence of edges in solution
            fineGraph         - the coarse graph object
            coarseningMatrix    - mapping from coarse to fine matrix
        """
 
        inflatedSolution = []
        weightedAdj = fineGraph.W  # this needs to be one step ahead
        
        # Getting coarsening Map:
        coarseningMap = self.coarseMatrixToMap(coarseningMatrix)

        # make sure it works for one vehicle
        numVehicles = len(solution)

        for vehicleIdx in range(numVehicles):
            coarseVehicleRoute = solution[vehicleIdx]

            inflatedRoute = self.inflateSingleRoute(coarseVehicleRoute, coarseningMap, weightedAdj)
            inflatedSolution.append(inflatedRoute)

        return inflatedSolution




    def coarseMatrixToMap(self, coarseningMatrix):

        # Child to Parent Mapping
        c, r = np.where((coarseningMatrix.todense() > 0) )
        coarsenMap = { i: [] for i in range(coarseningMatrix.shape[0]) }
 
        for (_c, _r) in zip(c, r):
            coarsenMap[_c] += [_r]

        return coarsenMap





    def inflateSingleRoute(self, route, coarsenMap, weightedAdj):
        """
            Expands Single Vehicle Route
            THIS ASSUMES A SINGLE BINARY DECISION AT EACH STEP
        """

        # reducing solution from [(a,b), (b,c), (c,d)] to [a,b,c,d]
        route = self.routeEdgeToNode(route)
        inflatedRoute = [coarsenMap[route[0]][0]]

        # Should assert first and last node belong in depot - requires knowledge of depots in coarse nodes
        # assert route[0] in self.depot and route[0]
        for routeStopIdx in range(1, len(route[1:]) + 1):
  
            #skipping first and last points (they are depots)
            nodeIdx = route[routeStopIdx]
            inflatedNode = coarsenMap[nodeIdx] 

            if len(inflatedNode) > 1: 
                # choice in direction - which node to go to first
                # Only works if no contraction neigboursa

                start = coarsenMap[route[routeStopIdx-1]]
                end = coarsenMap[route[routeStopIdx+1]]

                assert len(start) == 1 and len(end) == 1

                node1 = inflatedNode[0]
                node2 = inflatedNode[1]

                # Collective travelled distance
                distance1 = weightedAdj[start[0], node1] + weightedAdj[end[0],node2]
                distance2 = weightedAdj[start[0], node2] + weightedAdj[end[0],node1]
            
                if distance2 <= distance1:
                    inflatedNode = [node2, node1]

            inflatedRoute.extend(inflatedNode)

        inflatedRoute = self.routeNodeToEdge(inflatedRoute)

        return inflatedRoute




    def routeEdgeToNode(self, route):
        """
            Changing route from [(a,b), (b,c), (c,d)] to [a,b,c,d]
        """
        reducedRoute = []

        # adding first vertex of each edge sequentially
        for edge in route:
            reducedRoute.append(edge[0])
        
        # adding last element
        reducedRoute.append(route[-1][1])

        return reducedRoute




    def routeNodeToEdge(self, route):
        """
            Changing route from [a,b,c,d] to [(a,b), (b,c), (c,d)]
        """

        reducedRoute = [(route[0], route[1])]

        for nodeIdx in range(1, len(route) - 1):
            reducedRoute.append((route[nodeIdx], route[nodeIdx+1]))
        
        return reducedRoute