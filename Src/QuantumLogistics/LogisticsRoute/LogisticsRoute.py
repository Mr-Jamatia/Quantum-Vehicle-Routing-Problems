import matplotlib.pyplot as plt
from QuantumLogistics.LogisticsRoute.GraphCoarsening import BlankCoarseningEngine
import numpy as np
import scipy as sp
import pygsp
import copy

class Route(object):
    def __init__(self, LogisticsGraph, coarseningEngine = None, **config):
        
        graph = LogisticsGraph.graph
        self.nodeCapacities = LogisticsGraph.nodeCapacities

        # Keeping the raw data as well
        self._context = {
            'graph': graph
        }

        self.graph = graph                                      # PyGSP graph object
        self.n = LogisticsGraph.n                               # Number of nodes
        self.depot = config["depot"]                            # ID of the depot (default 0)
        self.cursor = config["depot"]                           # Current location of the cursor vehicle
        self.vehicles = config["vehicles"]                      # Number of vehicle
        self.truckCapacity = config["truckCapacity"]            # value of maximum truck capacity
        self.coords = getattr(graph, 'coords', [])              # Coordinates of the nodes
        self.routes = None                                      # Calculated Routes
        self.solution = None

        # Coarsening Parameters:
        self.coarsen = False

        if coarseningEngine == None:
            self.coarseningEngine = BlankCoarseningEngine()
        else:
            self.coarseningEngine = coarseningEngine
            
        self.coarsenRate = self.coarseningEngine.rate
        
        #Must ADD Capacities and Time Windows

    def __call__(self, ):
        pass
    
    
    def visualiseSolution(self, routeSolution, colormap = "hsv", saveImgFilepath = False):
        try:
            routes = routeSolution
            [xc, yc] = self.graph.coords.T
            plt.figure()
            plt.scatter(xc, yc, s=200)
            # for i in range(len(xc)):
            #     plt.annotate(i, (xc[i] + 0.15, yc[i]), size=16, color="r")

            i = 0
            for x, y in zip(xc, yc):
                plt.annotate(i, (x + 0.075, y), size=16, color="r")
                i += 1
            
            plt.plot(xc[0], yc[0], "r*", ms=20)
            plt.grid()

            vehicle_cmap = self.get_cmap(len(routes) + 1, name=colormap)
            for vehicle in range(len(routes)):
                tour = routes[vehicle]
                color = vehicle_cmap(vehicle)
                for hop in tour:
                    _from, _to = hop

                    plt.arrow(
                        xc[_from],
                        yc[_from],
                        xc[_to] - xc[_from],
                        yc[_to] - yc[_from],
                        length_includes_head=True,
                        head_width=0.02,
                        color = color
                    )

            if not saveImgFilepath:
                #print("THIS IS SHOWING THE THING HERE")
                plt.show()
            else:
                print("SAVING FIGURE")
                plt.savefig(saveImgFilepath)
        except:
            print("error when visualising route")
        return

    def visualiseGraph(self):
        pygsp.plotting.plot_graph(self.graph)
        input("Press any button to continue")
        return

    def evalutateKPIS(self, solution):
        cost = self.calculateCost(solution)
        return


    def get_cmap(self, n, name='hsv'):
        '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct 
        RGB color; the keyword argument name must be a standard mpl colormap name.'''
        return plt.cm.get_cmap(name, n)


    def pygsp_graph(self):
        """
            Returns the source graph PyGSP object
        """
        return self._context['graph']


    def graphEdges2Dict(self, graph):
        edge_list = graph.get_edge_list()
        n1, n2, w = edge_list
        assert len(n1) == len(n2) == len(w)
        return { (n1[i], n2[i]):w[i] for i in range(len(n1)) }



    def calculateCost(self, solution):
        """
            Needs to be checked fundamentally
        """
        _graph = self.pygsp_graph()
        edl = self.graphEdges2Dict(_graph)
        cost = 0
        for route in solution:
            for (_from, _to) in route:
                cost += edl.get((_from, _to), edl.get((_to, _from), 0) )

        return cost



    def recordMetaData(self):
        """
            Add important details to self.metaData for later analysis
        """
        raise NotImplementedError


    def setSolution(self):
         #Solution to be in form:
        #  [  [list vehicle1 nodes],
        #     [list vehicle2 nodes],
        #     [list vehicle3 nodes],]

        raise NotImplementedError



    def coarsenGraph(self):
        """
            Coarsens the graph using the coarseningEngine defined in the route instantiation
        """
        # General parameters
        coarseningRate = self.coarseningEngine.rate
        initialGraphSize = self.n
        newGraphSize = initialGraphSize
        fineNodeCapacities = self.nodeCapacities

        # History lists
        self.originalGraph = copy.deepcopy(self.graph)   #pygsp object
        self.coarsenGraphHistory = [self.originalGraph]
        self.coarsenMappingHistory = [sp.sparse.eye(self.originalGraph.N, format="csc")]

        # Setting graph variable
        graphToCoarsen = self.graph

        # Coarsening graphs - probably need to do metrics here to compare the original to final
        while newGraphSize > coarseningRate * initialGraphSize:
            # Coarsening
            coarsenedGraph, fineToCoarseMapping = self.coarseningEngine.coarsen(graphToCoarsen, self.depot, fineNodeCapacities, self.truckCapacity)

            # updating node capacities
            coarseNodeCapacities = self.propogateNodeCapacities(fineNodeCapacities, fineToCoarseMapping)

            # Saving history and iterating
            self.coarsenGraphHistory.append(coarsenedGraph)
            self.coarsenMappingHistory.append(fineToCoarseMapping)
            graphToCoarsen = coarsenedGraph
            coarseGraphSize = coarsenedGraph.N

            if coarseGraphSize == newGraphSize:
                print("Has not decreased in size, terminating now: ")
                break
            
            newGraphSize = coarseGraphSize
            fineNodeCapacities = coarseNodeCapacities

            plotCoords = False
            if plotCoords == True:
                plt.scatter(self.originalGraph.coords[:,0], self.originalGraph.coords[:,1])
                plt.scatter(coarsenedGraph.coords[:,0], coarsenedGraph.coords[:,1])
                plt.show()
                
        self.graph = graphToCoarsen
        self.nodeCapacities = fineNodeCapacities
        
        print("Final coarse graph has {0} nodes".format(self.graph.N))

        return


    def propogateNodeCapacities(self, fineNodeCapacities, fineToCoarseMapping):
        """
            Updating coarse node capacities
        """
        rows,cols = fineToCoarseMapping.nonzero() # When working, it's 13 x 14 i.e. 14 nodes coarsened to 13
        coarseNodeQty = max(cols) # Thus, this is max of the 14 elements [0...13] ie 13 ]---.
        coarseNodeCapacities = np.zeros(coarseNodeQty)      #                               |  TODO: In case of un-successful
                                                            #                               |  coarsening, this fineToCoarseMapping
        for row,col in zip(rows,cols):                      #                               |  is a square matrix, raising problems
            coarseNodeCapacities[row] += fineNodeCapacities[col]   #                    < --'  $ python3 src/sample.py
        return coarseNodeCapacities





    def inflateGraph(self, solution):
        """
            Inflates solution from solver to coarsen engine
        """

        # need to inflate through graphs:
        coarseGraphSol = solution #- list of lists for each vehicle

        inflatedRoutes = coarseGraphSol

        # Stepping through history
        for graphIdx in range(len(self.coarsenGraphHistory) - 1, 0, -1):
            coarsenedGraph = self.coarsenGraphHistory[graphIdx-1]
            coarseningMatrix = self.coarsenMappingHistory[graphIdx]
            inflatedSolution = self.coarseningEngine.inflateSolution(coarseGraphSol, coarsenedGraph, coarseningMatrix)
            inflatedRoutes.append(inflatedSolution)

            # Setting current inflated to new coarse:
            coarseGraphSol = inflatedSolution
    
        return  inflatedSolution




        